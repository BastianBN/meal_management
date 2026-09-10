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
    "lunch", "food", "plats", "specialites", "notre-carte", "la-carte", "les-menus"
]

# Domaines d'annuaires ou réseaux sociaux à ignorer pour trouver le site officiel
EXCLUDED_DOMAINS = {
    "tripadvisor.fr", "tripadvisor.com", "thefork.fr", "thefork.com", "lafourchette.com",
    "pagesjaunes.fr", "yelp.fr", "yelp.com", "ubereats.com", "deliveroo.fr", 
    "just-eat.fr", "facebook.com", "instagram.com", "linternaute.com", "mapstr.com",
    "societe.com", "infogreffe.fr", "lefigaro.fr", "actu.fr", "wikipedia.org", "google.com"
}


def build_google_maps_url(name: str, address: Optional[str] = None) -> str:
    """Construit un lien direct vers la fiche Google Maps / Google Card du restaurant."""
    query_parts = [name]
    if address:
        query_parts.append(address)
    query_str = " ".join(query_parts)
    encoded = urllib.parse.quote_plus(query_str)
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"


async def is_url_alive(url: str, timeout: float = 4.0) -> bool:
    """Vérifie si une URL est active et accessible (statut HTTP < 400)."""
    if not url or not url.startswith("http"):
        return False
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, follow_redirects=True, verify=False) as client:
            resp = await client.get(url)
            return resp.status_code < 400
    except Exception:
        return False


async def search_restaurant_website(name: str, city_or_address: Optional[str] = None) -> Optional[str]:
    """
    Recherche le site officiel du restaurant en cas d'absence d'URL ou d'URL morte dans OpenStreetMap.
    Extrait les liens réels de DuckDuckGo avec décodage des redirections uddg.
    """
    clean_name = re.sub(r"[^\w\s-]", " ", name).strip()
    query_parts = ["restaurant", f'"{clean_name}"']
    if city_or_address:
        # Extraire la ville ou un extrait court
        city_match = re.search(r"\b(\d{5}\s+[\w\s-]+|[A-Z][a-zéèêàïç\-]+)\b", city_or_address)
        if city_match:
            query_parts.append(city_match.group(0))
        else:
            query_parts.append(city_or_address[:30])
    query = " ".join(query_parts)

    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=6.0, follow_redirects=True) as client:
            resp = await client.post(url, data=params)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Liens de résultats DuckDuckGo
            links = soup.select(".result__body a.result__url, .result__body h2 a.result__snippet")
            for link in links:
                href = link.get("href", "")
                actual_url = None

                # Décoder le redirect DuckDuckGo uddg
                if "uddg=" in href:
                    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    candidate = parsed_qs.get("uddg", [None])[0]
                    if candidate:
                        actual_url = candidate
                elif href.startswith("http"):
                    actual_url = href

                if actual_url:
                    parsed = urllib.parse.urlparse(actual_url)
                    domain = parsed.netloc.lower()
                    if not any(ex in domain for ex in EXCLUDED_DOMAINS):
                        clean_url = f"{parsed.scheme}://{parsed.netloc}"
                        if await is_url_alive(clean_url):
                            return clean_url

    except Exception as exc:
        logger.debug(f"Recherche DuckDuckGo pour '{name}': {exc}")
    
    return None


def extract_french_lunch_formulas(text: str) -> List[Dict[str, str]]:
    """
    Analyse le texte pour identifier les formules midi, plats du jour et tarifs en euros.
    """
    formulas = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    price_regex = re.compile(r"(\d{1,2}(?:[.,]\d{2})?)\s*(?:€|EUR|euros?)", re.IGNORECASE)

    formula_patterns = [
        re.compile(r"(formule\s+midi|formule\s+déjeuner|menu\s+du\s+midi|menu\s+déjeuner|menu\s+du\s+jour)", re.IGNORECASE),
        re.compile(r"(plat\s+du\s+jour|plat\s+du\s+midi|suggestion\s+du\s+jour)", re.IGNORECASE),
        re.compile(r"(entrée\s*\+\s*plat\s*\+\s*dessert)", re.IGNORECASE),
        re.compile(r"(entrée\s*\+\s*plat|plat\s*\+\s*dessert)", re.IGNORECASE),
        re.compile(r"(formule\s+express|menu\s+express|menu\s+bistrot)", re.IGNORECASE),
    ]

    for i, line in enumerate(lines):
        for pattern in formula_patterns:
            match = pattern.search(line)
            if match:
                title = match.group(0).capitalize()
                price = None
                description_parts = []
                
                # Chercher le prix sur la même ligne
                price_match = price_regex.search(line)
                if price_match:
                    price = f"{price_match.group(1).replace('.', ',')} €"
                
                # Chercher dans les 3 lignes suivantes
                for next_idx in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[next_idx]
                    if not price:
                        next_price_match = price_regex.search(next_line)
                        if next_price_match:
                            price = f"{next_price_match.group(1).replace('.', ',')} €"
                            continue
                    if len(next_line) < 90 and not any(p.search(next_line) for p in formula_patterns):
                        description_parts.append(next_line)

                desc = " • ".join(description_parts[:2]) if description_parts else None

                if not any(f["name"].lower() == title.lower() for f in formulas):
                    formulas.append({
                        "name": title,
                        "price": price or "Tarif sur place",
                        "description": desc
                    })
                break

    return formulas[:4]


def extract_fallback_dishes(soup: BeautifulSoup) -> Optional[str]:
    """Extrait des suggestions de plats ou sections de carte quand aucune formule formelle n'est détectée."""
    dishes = []
    # Chercher des éléments de liste ou paragraphes courts contenant des noms de plats
    for el in soup.find_all(["li", "p", "h3", "h4"]):
        t = el.get_text(strip=True)
        if 15 < len(t) < 70 and not any(k in t.lower() for k in ["cookie", "politique", "mentions", "copyright", "tous droits"]):
            dishes.append(t)
            if len(dishes) >= 3:
                break
    
    if dishes:
        return "À la carte : " + " • ".join(dishes)
    return "Carte et suggestions du chef disponibles sur place."


async def scrape_restaurant_menu(
    name: str, 
    website_url: Optional[str] = None, 
    city_or_address: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str], List[Dict[str, str]], str]:
    """
    Explore le site web du restaurant, localise la page carte/menu (ou PDF),
    extrait les formules et renvoie l'URL Google Maps garantie.
    Retourne (website_url, menu_url, menu_summary, lunch_formulas, google_maps_url).
    """
    google_maps_url = build_google_maps_url(name, city_or_address)

    # 1. Vérifier si l'URL existante est bien vivante
    if website_url:
        alive = await is_url_alive(website_url)
        if not alive:
            logger.info(f"Lien OSM mort pour {name} ({website_url}), tentative de recherche web...")
            website_url = None

    # 2. Découverte de l'URL si manquante ou morte
    if not website_url:
        website_url = await search_restaurant_website(name, city_or_address)

    if not website_url:
        return None, None, "Carte et formules du midi consultables sur place ou sur la fiche Google.", [], google_maps_url

    menu_url = None
    menu_summary = None
    lunch_formulas = []

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=7.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(website_url)
            if resp.status_code >= 400:
                return None, None, "Carte consultable au restaurant et sur Google.", [], google_maps_url

            soup = BeautifulSoup(resp.text, "html.parser")

            # 3. Chercher un lien direct vers un PDF ou vers la page Menu / Carte
            pdf_link = None
            html_menu_link = None

            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                link_text = a_tag.get_text(separator=" ", strip=True).lower()
                href_lower = href.lower()

                # Détection PDF
                if href_lower.endswith(".pdf") or ".pdf?" in href_lower:
                    if any(kw in link_text or kw in href_lower for kw in MENU_LINK_KEYWORDS):
                        pdf_link = urllib.parse.urljoin(website_url, href)
                        break

                # Détection page HTML de menu
                if not html_menu_link and any(kw in link_text or kw in href_lower for kw in MENU_LINK_KEYWORDS):
                    html_menu_link = urllib.parse.urljoin(website_url, href)

            if pdf_link and await is_url_alive(pdf_link):
                menu_url = pdf_link
            elif html_menu_link and await is_url_alive(html_menu_link):
                menu_url = html_menu_link

            # 4. Récupérer le contenu de la page Menu pour analyse
            target_url = menu_url if (menu_url and not menu_url.endswith(".pdf")) else website_url
            if menu_url and menu_url != website_url and not menu_url.endswith(".pdf"):
                try:
                    menu_resp = await client.get(menu_url)
                    if menu_resp.status_code == 200:
                        soup = BeautifulSoup(menu_resp.text, "html.parser")
                except Exception:
                    pass

            for tag in soup(["script", "style", "svg", "noscript", "footer", "nav"]):
                tag.decompose()

            page_text = soup.get_text(separator="\n", strip=True)

            # 5. Extraction des formules midi
            lunch_formulas = extract_french_lunch_formulas(page_text)

            # 6. Résumé
            if lunch_formulas:
                items_str = ", ".join([f"{f['name']} ({f['price']})" for f in lunch_formulas])
                menu_summary = f"Formules repérées : {items_str}"
            elif menu_url and menu_url.endswith(".pdf"):
                menu_summary = "Carte complète du midi disponible en téléchargement PDF."
            else:
                menu_summary = extract_fallback_dishes(soup)

    except Exception as exc:
        logger.debug(f"Erreur scraping pour {name} ({website_url}): {exc}")
        menu_summary = "Carte et formules du midi disponibles sur place."

    return website_url, menu_url, menu_summary, lunch_formulas, google_maps_url
