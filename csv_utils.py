import csv
import os
from datetime import datetime
from typing import List

from _types import Paper

def get_papers_from_csv(csv_path: str) -> List[Paper]:
    """Read papers from CSV if it exists."""
    papers = []
    if not os.path.exists(csv_path):
        return papers
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert string representation of list back to list for authors
            authors = row['authors'].strip('[]').split(',') if row['authors'] else []
            authors = [a.strip().strip("'") for a in authors if a.strip()]
            
            paper = Paper(
                title=row['title'],
                url=row['url'],
                authors=authors,
                abstract=row['abstract'],
                published=datetime.strptime(row['published'], '%Y-%m-%d').date() if row['published'] else None,
                explored=row['explored'].lower() == 'true',
                summary=row['summary'],
                focus=row['focus']
            )
            papers.append(paper)
    return papers

def write_papers_to_csv(csv_path: str, papers: List[Paper]) -> None:
    """Write papers to CSV file."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # If file exists, read existing papers to merge with new ones
    existing_papers = get_papers_from_csv(csv_path) if os.path.exists(csv_path) else []
    
    # Create a dictionary of existing papers by title for easy lookup
    existing_dict = {p.title: p for p in existing_papers}
    
    # Update existing papers and add new ones
    for paper in papers:
        existing_dict[paper.title] = paper
    
    # Convert to final list
    final_papers = list(existing_dict.values())
    
    # Write all papers to CSV
    fieldnames = ['title', 'url', 'authors', 'abstract', 'published', 'explored', 'summary', 'focus']
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for paper in final_papers:
            writer.writerow({
                'title': paper.title,
                'url': paper.url,
                'authors': str(paper.authors),
                'abstract': paper.abstract,
                'published': paper.published.strftime('%Y-%m-%d') if paper.published else '',
                'explored': str(paper.explored),
                'summary': paper.summary,
                'focus': paper.focus
            })
