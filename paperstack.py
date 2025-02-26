import argparse
import os

from arxiv_utils import fill_papers_with_arxiv, search_arxiv_as_paper
from csv_utils import get_papers_from_csv, write_papers_to_csv
from openai_utils import (
    get_focus_label_from_abstract,
    get_openai_client,
    summarize_abstract_with_openai,
)
from scholar_utils import get_recommended_arxiv_ids_from_semantic_scholar
from obsidian_utils import write_papers_table_to_markdown

ARXIV_SEARCH = """\
"adversarial attacks" OR "language model attacks" OR "LLM vulnerabilities" OR \
"AI security" OR "machine learning security" OR "jailbreak" OR "bypassing AI" OR \
"data synthesis" OR "synthetic data" OR "data generation"\
"""


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output-csv",
        type=str,
        default="papers.csv",
        help="Path to output CSV file",
    )
    parser.add_argument(
        "--openai-token",
        type=str,
        default=None,
        help="OpenAI token (optional)",
    )
    parser.add_argument("--arxiv-search-query", type=str, default=ARXIV_SEARCH)
    parser.add_argument("--search-arxiv", action="store_true", default=False)
    parser.add_argument("--search-semantic-scholar", action="store_true", default=False)
    parser.add_argument(
        "--output-obsidian",
        type=str,
        default="papers.md",
        help="Path to output Obsidian folder"
    )

    args = parser.parse_args()

    print("[+] Arxivist")

    openai_client = None
    if args.openai_token:
        openai_client = get_openai_client(args.openai_token)
        print(" |- OpenAI client initialized")
    else:
        print(" |- No OpenAI token provided; skipping OpenAI operations")

    print(f" |- Reading existing papers from CSV [{args.output_csv}]")
    papers = get_papers_from_csv(args.output_csv)

    if not all([p.has_arxiv_props() for p in papers]):
        print(" |- Filling in missing data from arXiv")
        papers = fill_papers_with_arxiv(papers)

    if args.search_arxiv:
        print(" |- Searching arXiv for new papers")
        existing_titles = [paper.title for paper in papers]
        for searched_paper in search_arxiv_as_paper(
            args.arxiv_search_query, max_results=10
        ):
            if searched_paper.title not in existing_titles:
                print(f"    |- {searched_paper.title[:50]}...")
                papers.append(searched_paper)

    if args.search_semantic_scholar:
        to_explore = [p for p in papers if not p.explored]
        if to_explore:
            print(" |- Getting related papers from Semantic Scholar")
            recommended_papers = get_recommended_arxiv_ids_from_semantic_scholar(papers)
            papers.extend(fill_papers_with_arxiv(recommended_papers))
            print(f"    |- {len(recommended_papers)} new papers")
        else:
            print(" |- All papers have been explored")

    if openai_client:
        print(" |- Generating summaries and focus labels using OpenAI")
        for paper in papers:
            if paper.abstract:
                paper.summary = summarize_abstract_with_openai(openai_client, paper.abstract)
                paper.focus = get_focus_label_from_abstract(openai_client, paper.abstract)
    else:
        print(" |- Skipping summary generation as no OpenAI token was provided")

    print(f" |- Writing papers to CSV [{args.output_csv}]")
    write_papers_to_csv(args.output_csv, papers)
    print(f" |- Done! Saved {len(papers)} papers to {args.output_csv}")

    if args.output_obsidian:
        print(f" |- Writing papers to Obsidian format [{args.output_obsidian}]")
        from obsidian_utils import write_papers_to_obsidian
        write_papers_to_obsidian(args.output_obsidian, papers)

    # Create the arxivist-papers.md file
    arxivist_file_path = os.path.join(args.output_obsidian, "arxivist-papers.md")
    print(f" |- Writing papers table to Markdown file [{arxivist_file_path}]")
    write_papers_table_to_markdown(arxivist_file_path, papers)


if __name__ == "__main__":
    main()
