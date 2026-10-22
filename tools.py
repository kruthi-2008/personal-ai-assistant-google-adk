import json
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import ast
import operator
import re


def calculator(expression: str) -> str:
    """Calculate a mathematical expression accurately.

    Use this tool for arithmetic, percentages, GST, and
    other numerical calculations.

    Args:
        expression: A mathematical expression, such as
            "12500 * 18 / 100".
    """

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")

            result = allowed_operators[type(node.op)](left, right)

            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Result is too large.")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](evaluate(node.operand))

        raise ValueError("Unsupported mathematical expression.")

    try:
        expression = expression.replace("₹", "").replace(",", "").strip()
        expression = re.sub(
            r"(\d+(?:\.\d+)?)%",
            r"(\1/100)",
            expression,
        )
        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree.body)

        if isinstance(result, float) and not result.is_integer():
            return f"{result:.10g}"

        return str(result)

    except Exception as error:
        return f"Calculation error: {error}"


def text_analyzer(text: str) -> dict:
    """Analyze text and return character, word, and sentence counts.

    Args:
        text: The text to analyze.
    """

    characters = len(text)
    words = len(text.split())
    sentences = [
        sentence
        for sentence in re.split(r"[.!?]+", text.strip())
        if sentence.strip()
    ]

    return {
        "characters": characters,
        "words": words,
        "sentences": len(sentences),
    }

def date_significance(date: str) -> str:
    """Find historical events, notable births, deaths, and
    observances associated with a date.

    Use this tool when the user asks what is important,
    special, or historically significant about a date.

    Args:
        date: A date such as "1947-08-15", "15/08/1947",
              or "15 August 1947".

    Returns:
        Historical information associated with that date,
        including source links when available.
    """

    # Parse the date entered by the user.
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %B %Y",
        "%B %d, %Y",
        "%m/%d/%Y",
    ]

    parsed_date = None

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(
                date.strip(), date_format
            ).date()
            break
        except ValueError:
            continue

    if parsed_date is None:
        return (
            "I couldn't understand that date. "
            "Please enter it as YYYY-MM-DD, "
            "for example 1947-08-15."
        )

    month = parsed_date.month
    day = parsed_date.day
    year = parsed_date.year

    # Request historical information from Wikimedia.
    url = (
        "https://api.wikimedia.org/feed/v1/wikipedia/en/"
        f"onthisday/all/{month:02d}/{day:02d}"
    )

    request = Request(
        url,
        headers={
            "User-Agent": "PersonalAIAssistantWorkshop/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return (
            "I couldn't retrieve date information right now. "
            "Please check your internet connection and try again. "
            f"Details: {error}"
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        return "The historical information service returned an invalid response."

    def format_entry(entry):
        event_year = entry.get("year", "Unknown year")
        description = entry.get("text", "No description available.")

        line = f"- {event_year}: {description}"

        pages = entry.get("pages", [])

        if pages:
            page = pages[0]
            page_url = (
                page.get("content_urls", {})
                .get("desktop", {})
                .get("page")
            )

            if page_url:
                line += f"\n  Source: {page_url}"

        return line

    # Combine selected events and general historical events.
    history = []
    seen = set()

    for category in ("selected", "events"):
        for entry in data.get(category, []):
            key = (entry.get("year"), entry.get("text"))

            if key not in seen:
                seen.add(key)
                history.append(entry)

    # Give priority to events explicitly listed for the year
    # the user entered.
    exact_year = [
        entry for entry in history
        if entry.get("year") == year
    ]

    other_events = [
        entry for entry in history
        if entry.get("year") != year
    ]

    result = [
        f"Date significance for {parsed_date.strftime('%d %B %Y')}",
        "",
    ]

    if exact_year:
        result.append(f"Events listed for {year}:")
        result.extend(format_entry(e) for e in exact_year[:3])
        result.append("")
    else:
        result.append(
            f"No historical event was explicitly listed for {year} "
            "in the returned events."
        )
        result.append("")

    if other_events:
        result.append(
            f"Other historical events on {day:02d}/{month:02d}:"
        )
        result.extend(
            format_entry(e) for e in other_events[:4]
        )
        result.append("")

    # Include other kinds of significance for that calendar date.
    for category, heading in [
        ("births", "Notable births"),
        ("deaths", "Notable deaths"),
        ("holidays", "Holidays and observances"),
    ]:
        entries = data.get(category, [])

        if entries:
            result.append(f"{heading}:")
            result.extend(format_entry(e) for e in entries[:2])
            result.append("")

    result.append(
        "Source: Wikimedia's On This Day feed. "
        "Events listed under other years happened on the same "
        "month and day, not necessarily in the requested year."
    )

    return "\n".join(result)
