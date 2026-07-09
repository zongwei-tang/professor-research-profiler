import httpx

from app.core.config import settings


def search_author(name: str):
    try:
        key = settings.semantic_scholar_api_key
        if not key:
            raise KeyError("SEMANTICS_SCHOLAR_API_KEY not found in environment variables.")
        response = httpx.get(
            'https://api.semanticscholar.org/graph/v1/author/search',
            headers={'x-api-key': key},
            params={'query': name, 'fields': 'name,authorId,affiliations,paperCount,citationCount,hIndex', 'limit': 5},
        )
        response.raise_for_status()
        return response.json().get('data')
    except httpx.HTTPError as e:
        print(f"Error searching for author: {e}")
        return None
    except KeyError as e:
        print(f"Error: {e}")
        return None


def get_papers(authorid: str):
    try:
        r = httpx.get(
            f'https://api.semanticscholar.org/graph/v1/author/{authorid}',
            params={'fields': 'papers.title,papers.year,papers.abstract,papers.citationCount,papers.authors,papers.fieldsOfStudy,papers.openAccessPdf,papers.venue'},
        )
        if r.status_code != 200:
            print(r.text)
            return None
        papers = r.json().get('papers') or []
        return [i for i in papers if i.get('abstract')]
    except httpx.HTTPError as e:
        print(f"Error fetching papers: {e}")
        return None


def compute(papers: list):
    top_5_cited = sorted(papers, key=lambda x: x.get('citationCount') or 0, reverse=True)[:5]
    by_year = {}
    coauthor = {}
    for i in papers:
        if i.get('year') in by_year:
            by_year[i.get('year')].append(i)
        else:
            by_year[i.get('year')] = [i]
        for j in i.get('authors', []):
            if (j.get('authorId'), j.get('name')) in coauthor:
                coauthor[(j.get('authorId'), j.get('name'))] += 1
            else:
                coauthor[(j.get('authorId'), j.get('name'))] = 1
    return top_5_cited, by_year, coauthor
