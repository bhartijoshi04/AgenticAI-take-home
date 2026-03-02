import re
import sys
import requests
from pathlib import Path
from typing import Tuple, Dict, Optional
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin

class ArxivService:
    """
    Service for fetching and processing arXiv papers.
    """
    
    def __init__(self, arxiv_base_url: str = "https://arxiv.org/html/"):
        self.arxiv_html_base = arxiv_base_url
    
    def extract_paper_id(self, input_string: str) -> str:
        """
        Extract arXiv paper ID from various input formats.
        """
        s = (input_string or "").strip()

        # Direct ID format
        if re.fullmatch(r"\d{4}\.\d{5}(v\d+)?", s):
            return s

        # Extract from abs/pdf URLs
        match = re.search(r"(?:abs|pdf)/(\d{4}\.\d{5}(?:v\d+)?)", s)
        if match:
            return match.group(1)

        # Extract from html URL
        match = re.search(r"arxiv.org/html/(\d{4}\.\d{5}(?:v\d+)?)", s)
        if match:
            return match.group(1)

        raise ValueError(f"Could not extract arXiv ID from: {s}")

    def fetch_html(self, paper_id: str) -> Tuple[str, str]:
        """
        Fetch HTML content from arXiv.
        """
        html_url = f"{self.arxiv_html_base}{paper_id}"
        
        try:
            response = requests.get(
                html_url,
                headers={"User-Agent": "arxiv-evaluator/1.0"},
                timeout=30,
                allow_redirects=True,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error fetching {html_url}: {e}") from e

        if response.status_code == 404:
            raise RuntimeError(f"arXiv HTML page not found (404): {html_url}")
        if not response.ok:
            raise RuntimeError(f"Failed to fetch arXiv HTML ({response.status_code}): {html_url}")

        if len(response.text) < 500:
            raise RuntimeError(f"Fetched HTML looks too small; possible error page: {html_url}")

        return html_url, response.text

    def _extract_math_blocks(self, html: str) -> Tuple[str, Dict[str, str]]:
        """Extract and replace math blocks with placeholders."""
        math_regex = re.compile(r"<math[^>]*>[\s\S]*?</math>", re.IGNORECASE)
        latex_map = {}

        def replace_math(match: re.Match) -> str:
            block = match.group(0)
            placeholder = f"ARXIVMATH{len(latex_map)}ARXIV"

            # Look for LaTeX annotation
            tex_match = re.search(
                r'<annotation[^>]*encoding="application/x-tex"[^>]*>([\s\S]*?)</annotation>',
                block,
                flags=re.IGNORECASE,
            )
            if tex_match:
                tex = tex_match.group(1).strip()
                is_display = 'display="block"' in block.lower()
                latex_map[placeholder] = f"\n\n$${tex}$$\n\n" if is_display else f"${tex}$"
                return placeholder

            # Fallback to alttext
            alt_match = re.search(r'alttext="([^"]+)"', block, flags=re.IGNORECASE)
            if alt_match:
                latex_map[placeholder] = f"${alt_match.group(1)}$"
                return placeholder

            return block

        processed_html = math_regex.sub(replace_math, html)
        return processed_html, latex_map

    def _absolutize_urls(self, soup: BeautifulSoup, base_url: str) -> None:
        """Convert relative URLs to absolute URLs."""
        for a in soup.find_all("a", href=True):
            a["href"] = urljoin(base_url, a["href"])
        for img in soup.find_all("img", src=True):
            img["src"] = urljoin(base_url, img["src"])

    def html_to_markdown(self, base_url: str, html: str) -> str:
        """
        Convert HTML to markdown while preserving mathematical notation.
        """
        html_with_placeholders, latex_map = self._extract_math_blocks(html)

        soup = BeautifulSoup(html_with_placeholders, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        self._absolutize_urls(soup, base_url)

        markdown = md(str(soup), heading_style="ATX")

        if latex_map:
            pattern = re.compile("|".join(re.escape(k) for k in latex_map.keys()))
            markdown = pattern.sub(lambda m: latex_map[m.group(0)], markdown)

        markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
        return markdown

    def get_paper_content(self, input_value: str) -> str:
        """
        Main entry point: fetch paper and convert to markdown.
        """
        paper_id = self.extract_paper_id(input_value)
        base_url, html = self.fetch_html(paper_id)
        return self.html_to_markdown(base_url, html)
