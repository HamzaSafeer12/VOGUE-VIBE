import mcp.server.fastmcp as fastmcp  # Direct import ki jagah aise use karein

# 1. Server ko mcp ke naam se hi initialize karein (Global variable)
mcp = fastmcp.FastMCP("CurrencyConverter")

@mcp.tool()
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Ek tool jo currency convert karta hai.
    """
    rates = {
        "USD": 1.0,
        "PKR": 280.0,
        "EUR": 0.92
    }

    f_curr = from_currency.upper()
    t_curr = to_currency.upper()

    if f_curr not in rates or t_curr not in rates:
        return f"Error: {f_curr} ya {t_curr} not found."

    amount_in_usd = amount / rates[f_curr]
    final_amount = amount_in_usd * rates[t_curr]

    return f"{amount} {f_curr} = {final_amount:.2f} {t_curr}"

# Yeh niche wala part mcp dev ke liye zaroori nahi hota lekin rehne dein
if __name__ == "__main__":
    mcp.run()