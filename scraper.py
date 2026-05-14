import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
import json
from datetime import datetime

console = Console()

def scrape_website(url):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        with console.status("[bold green]Scraping Data...[/bold green]"):
            response = session.get(url, timeout=10)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        
        data['url'] = url
        data['title'] = soup.title.string if soup.title else 'No title'
        data['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        data['headings'] = {
            'h1': len(soup.find_all('h1')),
            'h2': len(soup.find_all('h2')),
            'h3': len(soup.find_all('h3'))
        }
        
        data['links'] = []
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link['href']
            if text and href:
                data['links'].append({
                    'text': text[:100],
                    'url': href[:200]
                })
        
        data['images'] = []
        for img in soup.find_all('img', src=True):
            data['images'].append({
                'alt': img.get('alt', 'No alt text')[:100],
                'src': img['src'][:200]
            })
        
        data['paragraphs'] = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 20:
                data['paragraphs'].append(text[:200])
        
        data['text_content'] = soup.get_text(separator=' ', strip=True)[:1000]
        
        console.print("[green]Scraping completed![/green]\n")
        return data
        
    except requests.RequestException as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

def display_all_results(data):
    console.print(Panel.fit(
        f"[bold cyan]{data['title']}[/bold cyan]\n"
        f"[yellow]{data['url']}[/yellow]\n"
        f"Scraped: {data['scraped_at']}",
        title="Page Info",
        border_style="cyan"
    ))
    
    stats = Table(title="Statistics", border_style="yellow")
    stats.add_column("Element", style="cyan")
    stats.add_column("Count", style="green", justify="right")
    
    stats.add_row("Total Links", str(len(data['links'])))
    stats.add_row("Total Images", str(len(data['images'])))
    stats.add_row("Total Paragraphs", str(len(data['paragraphs'])))
    stats.add_row("H1 Headings", str(data['headings']['h1']))
    stats.add_row("H2 Headings", str(data['headings']['h2']))
    stats.add_row("H3 Headings", str(data['headings']['h3']))
    
    console.print(stats)
    console.print()
    
    if data['links']:
        table = Table(title="Links", border_style="yellow")
        table.add_column("Text", style="cyan")
        table.add_column("URL", style="green")
        for link in data['links'][:10]:
            table.add_row(link['text'], link['url'])
        console.print(table)
        console.print()
    else:
        console.print("[yellow]No links found[/yellow]\n")
    
    if data['images']:
        table = Table(title="Images", border_style="yellow")
        table.add_column("Alt Text", style="cyan")
        table.add_column("Source", style="green")
        for img in data['images'][:10]:
            table.add_row(img['alt'], img['src'])
        console.print(table)
        console.print()
    else:
        console.print("[yellow]No images found[/yellow]\n")
    
    if data['paragraphs']:
        console.print("[bold]Paragraphs:[/bold]")
        for i, para in enumerate(data['paragraphs'][:5], 1):
            console.print(f"\n[cyan]Paragraph {i}:[/cyan]")
            console.print(para)
        console.print()
    else:
        console.print("[yellow]No paragraphs found[/yellow]\n")
    
    console.print(Panel(
        data['text_content'],
        title="Page Text Content",
        border_style="green"
    ))

def save_json(data):
    filename = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    save_data = {k: v for k, v in data.items() if k != 'text_content'}
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]Saved to {filename}[/green]")

def main():
    console.print(Panel.fit(
    "          [bold cyan]Simple Web Scraper[/bold cyan]          \n"
    "    [yellow]Extract data from any website easily[/yellow]    ",
    border_style="cyan"
))
    
    url = Prompt.ask("\n[bold green]Enter URL to scrape[/bold green]")
    
    if not url.startswith('http'):
        url = 'https://' + url
        console.print(f"[yellow]Added https:// {url}[/yellow]")
    
    data = scrape_website(url)
    
    if data:
        display_all_results(data)
        
        save = Prompt.ask("\n[bold]Save data as JSON?[/bold]", choices=['y', 'n'])
        if save == 'y':
            save_json(data)
        
        console.print("\n[bold green]Thank You![/bold green]")
    else:
        console.print("[red]Failed to scrape the website.[/red]")

if __name__ == "__main__":
    main()