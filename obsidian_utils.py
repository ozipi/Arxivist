import os
from datetime import datetime
from typing import List
from _types import Paper

def write_papers_to_obsidian(output_dir: str, papers: List[Paper]) -> None:
    """Write papers to Obsidian markdown files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for paper in papers:
        if not paper.title:
            continue
            
        # Create a safe filename from the title
        safe_title = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in paper.title)
        filename = os.path.join(output_dir, f"{safe_title}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Write frontmatter
            f.write("---\n")
            f.write(f"title: {paper.title}\n")
            if paper.url:
                f.write(f"url: {paper.url}\n")
            if paper.published:
                f.write(f"date: {paper.published.strftime('%Y-%m-%d')}\n")
            if paper.authors:
                f.write(f"authors: {', '.join(paper.authors)}\n")
            if paper.focus:
                f.write(f"focus: {paper.focus.value}\n")
            f.write("---\n\n")
            
            # Write content
            if paper.summary:
                f.write("## Summary\n")
                f.write(f"{paper.summary}\n\n")
            
            if paper.abstract:
                f.write("## Abstract\n")
                f.write(f"{paper.abstract}\n")

def write_papers_table_to_markdown(output_file: str, papers: List[Paper]) -> None:
    """Write a Markdown table of papers to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Arxivist Papers\n\n")
        f.write("| Title | Authors | Published | URL | Summary | Focus |\n")
        f.write("|-------|---------|-----------|-----|---------|-------|\n")

        for paper in papers:
            # Create an internal link for Obsidian
            title_link = f"[[{paper.title}]]" if paper.title else "N/A"
            authors = ", ".join(paper.authors) if paper.authors else "N/A"
            published_date = paper.published.strftime('%Y-%m-%d') if paper.published else "N/A"
            summary = paper.summary if paper.summary else "N/A"
            focus = paper.focus.value if paper.focus else "N/A"

            f.write(f"| {title_link} | {authors} | {published_date} | {paper.url} | {summary} | {focus} |\n")