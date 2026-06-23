import bs4
import requests
from x_client_transaction import ClientTransaction
from x_client_transaction.utils import generate_headers, get_ondemand_file_url, handle_x_migration


def get_tid(cookies: dict[str, str] | None = None):
    session = requests.Session()
    session.headers = generate_headers()  # type: ignore
    # X now serves a brand new logged-out web client (x-web/x-web, a Vite build)
    # that no longer ships the `ondemand.s` chunk the transaction-id algorithm
    # relies on. The legacy `responsive-web/client-web` SPA (which still contains
    # it) is only returned for authenticated sessions, so forward the caller's
    # cookies here to keep getting a page `get_ondemand_file_url` can parse.
    if cookies:
        for key, value in cookies.items():
            session.cookies.set(key, value, domain=".x.com")
    home_page_response = handle_x_migration(session=session)
    home_page = session.get(url="https://x.com")
    home_page_response = bs4.BeautifulSoup(home_page.content, "html.parser")
    ondemand_file_url = get_ondemand_file_url(response=home_page_response)
    ondemand_file = session.get(url=ondemand_file_url)  # type: ignore
    ondemand_file_response = bs4.BeautifulSoup(ondemand_file.content, "html.parser")
    ct = ClientTransaction(home_page_response=home_page_response, ondemand_file_response=ondemand_file_response)
    return ct
