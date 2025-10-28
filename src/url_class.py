from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.parse import urlparse

@dataclass
class Code:
    link: str
    namespace: str = ""

@dataclass
class Dataset:
    link: str
    namespace: str = ""
    repo: str = ""
    rev: str = ""

@dataclass
class Model:
    # www.huggingface.co\namespace\repo\rev
    link: str 
    namespace: str = ""
    repo: str = ""
    rev: str = ""

@dataclass
class ProjectGroup:
    code: Optional[Code] = None
    dataset: Optional[Dataset] = None
    model: Optional[Model] = None

def parse_huggingface_url(url: str) -> Tuple[str, str, str]:
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid Hugging Face URL: {url}")
    namespace, repo = parts[0], parts[1]
    rev = "main"
    if len(parts) >= 4 and parts[2] == "tree":
        rev = parts[3]
    return namespace, repo, rev

def parse_dataset_url(url: str) -> str:
    """
    Parse a dataset URL and return the appropriate identifier for loading.
    
    - Hugging Face datasets: returns only the repo name
        Example: 
            https://huggingface.co/datasets/stanfordnlp/imdb -> "imdb"
            https://huggingface.co/datasets/glue -> "glue"
    
    - GitHub repos: returns the full URL (used directly for git clone)
        Example:
            https://github.com/zalandoresearch/fashion-mnist -> "https://github.com/zalandoresearch/fashion-mnist"
    
    Raises:
        ValueError: if the URL is not recognized.
    """
    parsed = urlparse(url)

    # Hugging Face case
    if "huggingface.co" in parsed.netloc:
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2 or parts[0] != "datasets":
            raise ValueError(f"Invalid Hugging Face dataset URL: {url}")
        return parts[-1]  # only the repo name, e.g. "imdb"

    # GitHub case
    if "github.com" in parsed.netloc:
        return url  # keep full URL for git clone

    raise ValueError(f"Unsupported dataset URL: {url}")
    

def parse_project_file(filepath: str) -> List[ProjectGroup]:
    """
    Parse a text file where each line has format:
        code_link,dataset_link,model_link

    Each line corresponds to a grouped set of links.
    Empty fields are allowed (e.g., ',,http://model.com').

    Args:
        filepath: Path to the input file.

    Returns:
        A list of ProjectGroup objects containing Code, Dataset, and/or Model.
    """
    project_groups: List[ProjectGroup] = []
    path = Path(filepath)

    with path.open("r", encoding="ASCII") as f:
        for line in f:
            line = line.strip()
            if not line:  # skip empty lines
                continue

            parts = [p.strip() for p in line.split(",")]
            # Pad with None if fewer than 3 entries
            while len(parts) < 3:
                parts.append("")

            code_link, dataset_link, model_link = parts

            # --- defaults to avoid "possibly unbound" ---
            ns = ""
            rp = ""
            rev = "main"
            data_repo = ""

            if model_link:
                ns, rp, rev = parse_huggingface_url(model_link)

            code = Code(code_link) if code_link else None

            dataset = None
            if dataset_link:
                data_repo = parse_dataset_url(dataset_link)
                dataset = Dataset(dataset_link, namespace="", repo=data_repo, rev="")
            
            model = None
            if model_link:
                ns, rp, rev = parse_huggingface_url(model_link)
                model = Model(model_link, ns, rp, rev)
            
            group = ProjectGroup(code=code, dataset=dataset, model=model)
            project_groups.append(group)

    return project_groups

parse_hf_dataset_url_repo = parse_dataset_url

def main():
    # Point to your test file
    filepath = Path("tests/test.txt")

    # Parse file
    groups = parse_project_file(str(filepath))

    # Print results
    print("Parsed project groups:\n")
    for i, group in enumerate(groups, start=1):
        print(f"Group {i}: {group}")


if __name__ == "__main__":
    url = "https://huggingface.co/openai-community/gpt2"
    ns, rp, rev = parse_huggingface_url(url)
    print(f"Namespace: {ns}, Repo: {rp}")
    # Output: Namespace: openai-community, Repo: gpt2