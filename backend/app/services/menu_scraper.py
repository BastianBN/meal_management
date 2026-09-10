import re
import urllib.parse
import logging
from typing import Dict, Any, List, Optional, Tuple
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Mots-clés pour repérer les liens de menu dans les balises <a>
MENU_LINK_KEYWORDS = [
    "carte", "menu", "formule", "dejeuner", "midi", "ardoise", "tarifs", 
    "lunch", "food", "plats", "specialites"
]

# Domaines d'annuaires à ignorer lors de la recherche du site officiel
EXCLUDED_DOMAINS = {
    "tripadvisor.fr", "tripadvisor.com", "thefork.fr", "thefork.com", "lafourchette.com",
    "pagesjaunes.fr", "yelp.fr", "yelp.com", "ubereats.com", "deliveroo.fr", 
    "just-eat.fr", "facebook.com", "instagram.com", "linternaute.com", "mapstr.com"
}


async def search_restaurant_website(name: str, city_or_address: Optional[str] = None) -> Optional[str]:
    """
    Recherche le site officiel du restaurant sur le web en cas d'absence d'URL dans OpenStreetMap.
    Utilise le moteur DuckDuckGo HTML sans clé d'API.
    """
    query_parts = ["restaurant", f'"{name}"']
    if city_or_address:
        query_parts.append(city_or_address)
    query = " ".join(query_parts)

    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=8.0, follow_redirects=True) as client:
            resp = await client.post(url, data=params)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            results = soup.select(".result__url")
            
            for res in results:
                raw_link = res.get_text(strip=True)
                if not raw_link.startswith("http"):
                    raw_link = "https://" + raw_link
                
                parsed = urllib.parse.urlparse(raw_link)
                domain = parsed.netloc.lower()
                
                # Vérifie que le domaine n'est pas un annuaire générique
                if not any(excluded in domain for excluded in EXCLUDED_DOMAINS):
                    return f"{parsed.scheme}://{parsed.netloc}"

    except Exception as exc:
        logger.debug(f"Erreur recherche web site pour '{name}': {exc}")
    
    return None


def extract_french_lunch_formulas(text: str) -> List[Dict[str, str]]:
    """
    Analyse le texte brut d'une page web pour identifier les formules midi
    (ex: Plat du jour, Entrée + Plat, Formule Midi, Tarifs en €).
    """
    formulas = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Regex pour capter les prix en euros (ex: 14.50€, 16 €, 18,90 EUR)
    price_regex = re.compile(r"(\d{1,2}(?:[.,]\d{2})?)\s*(?:€|EUR|euros?)", re.IGNORECASE)

    # Motifs caractéristiques de formules déjeuners françaises
    formula_patterns = [
        re.compile(r"(formule\s+midi|formule\s+déjeuner|menu\s+du\s+midi|menu\s+déjeuner)", re.IGNORECASE),
        re.compile(r"(plat\s+du\s+jour|plat\s+du\s+midi)", re.IGNORECASE),
        re.compile(r"(entrée\s*\+\s*plat\s*\+\s*dessert)", re.IGNORECASE),
        re.compile(r"(entrée\s*\+\s*plat|plat\s*\+\s*dessert)", re.IGNORECASE),
        re.compile(r"(menu\s+du\s+jour|formule\s+express)", re.IGNORECASE),
    ]

    for i, line in enumerate(lines):
        for pattern in formula_patterns:
            match = pattern.search(line)
            if match:
                title = match.group(0).capitalize()
                
                # Chercher le prix sur la ligne ou les 2 lignes suivantes
                price = None
                description_parts = []
                
                # Chercher sur la ligne courante
                price_match = price_regex.search(line)
                if price_match:
                    price = f"{price_match.group(1).replace('.', ',')} €"
                
                # Regarder les lignes adjacentes (souvent le tarif est en dessous)
                for next_idx in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[next_idx]
                    if not price:
                        next_price_match = price_regex.search(next_line)
                        if next_price_match:
                            price = f"{next_price_match.group(1).replace('.', ',')} €"
                            continue
                    if len(next_line) < 80 and not any(p.search(next_line) for p in formula_patterns):
                        description_parts.append(next_line)

                desc = " • ".join(description_parts[:2]) if description_parts else None

                # Éviter les doublons
                if not any(f["name"].lower() == title.lower() for f in formulas):
                    formulas.append({
                        "name": title,
                        "price": price or "Tarif sur place",
                        "description": desc
                    })
                break

    return formulas[:4]


async def scrape_restaurant_menu(
    name: str, 
    website_url: Optional[str] = None, 
    city_or_address: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str], List[Dict[str, str]]]:
    """
    Explore le site web du restaurant, localise la page carte/menu,
    extrait les formules du midi et produit un résumé lisible.
    Retourne (website_url, menu_url, menu_summary, lunch_formulas).
    """
    # 1. Découverte de l'URL si absente
    if not website_url:
        website_url = await search_restaurant_website(name, city_or_address)

    if not website_url:
        return None, None, "Menu consultable directement sur place.", []

    menu_url = None
    menu_summary = None
    lunch_formulas = []

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=8.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(website_url)
            if resp.status_code != 200:
                return website_url, None, "Site web accessible. Carte du midi disponible au restaurant.", []

            soup = BeautifulSoup(resp.text, "html.parser")

            # Retirer scripts, styles, svg
            for tag in soup(["script", "style", "svg", "noscript", "footer", "nav"]):
                tag.decompose()

            # 2. Chercher un lien vers la page Menu / Carte
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                link_text = a_tag.get_text(separator=" ", strip=True).lower()
                href_lower = href.lower()

                if any(kw in link_text or kw in href_lower for kw in MENU_LINK_KEYWORDS):
                    # Résoudre URL absolue
                    menu_url = urllib.parse.urljoin(website_url, href)
                    break

            # 3. Récupérer le contenu de la page Menu (ou de la page d'accueil si pas de sous-page)
            target_url = menu_url if menu_url else website_url
            if menu_url and menu_url != website_url:
                try:
                    menu_resp = await client.get(menu_url)
                    if menu_resp.status_code == 200:
                        soup = BeautifulSoup(menu_resp.text, "html.parser")
                        for tag in soup(["script", "style", "svg", "noscript"]):
                            tag.decompose()
                except Exception:
                    pass

            page_text = soup.get_text(separator="\n", strip=True)

            # 4. Extraire les formules midi spécifiques
            lunch_formulas = extract_french_lunch_formulas(page_text)

            # 5. Créer un résumé concis
            if lunch_formulas:
                items_str = ", ".join([f"{f['name']} ({f['price']})" for f in lunch_formulas])
                menu_summary = f"Formules repérées : {items_str}"
            else:
                # Extraire quelques lignes parlantes ou plats
                short_lines = [l for l in page_text.split("\n") if 15 < len(l) < 90 and not l.startswith("http")]
                if short_lines:
                    menu_summary = "Extraits de la carte : " + " • ".join(short_lines[:3])
                else:
                    menu_summary = "Carte et suggestions du chef disponibles sur le site et sur place."

    except Exception as exc:
        logger.debug(f"Erreur scraping pour {name} ({website_url}): {exc}")
        menu_summary = "Site en ligne. Carte du jour disponible au restaurant."

    return website_url, menu_url, menu_summary, lunch_formulas
