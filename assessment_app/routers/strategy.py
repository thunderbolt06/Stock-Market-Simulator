from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from assessment_app.models.models import Portfolio, PortfolioRequest, Strategy, TickData
from assessment_app.service.auth_service import get_current_user

router = APIRouter()


@router.get("/strategies", response_model=list[Strategy])
async def get_strategies(current_user_id: str = Depends(get_current_user)) -> list[Strategy]:
    """
    Get all strategies available. You do not need to implement this.
    """
    return [
        Strategy(
            id="0",
            name="default"
        )
    ]


@router.post("/portfolio", response_model=Portfolio)
async def create_portfolio(portfolio_request: PortfolioRequest, current_user_id: str = Depends(get_current_user)) -> Portfolio:
    """
    Create a new portfolio and initialise with funds with empty holdings.
    """
    new_portfolio = Portfolio(user_id=current_user_id, cash_remaining=portfolio_request.cash_remaining)
    await new_portfolio.save()
    return new_portfolio


@router.get("/portfolio/{portfolio_id}", response_model=Portfolio)
async def get_portfolio_by_id(portfolio_id: str, current_ts: datetime, current_user_id: str = Depends(get_current_user)) -> Portfolio:
    """
    Get specified portfolio for the current user.
    """
    portfolio = await Portfolio.find_one(Portfolio.user_id == current_user_id, Portfolio.id == portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio


@router.delete("/portfolio/{portfolio_id}", response_model=Portfolio)
async def delete_portfolio(portfolio_id: str, current_user_id: str = Depends(get_current_user)) -> Portfolio:
    """
    Delete the specified portfolio for the current user.
    """
    portfolio = await Portfolio.find_one(Portfolio.user_id == current_user_id, Portfolio.id == portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    await portfolio.delete()
    return portfolio



@router.get("/portfolio-net-worth", response_model=float)
async def get_net_worth(portfolio_id: str, current_user_id: str = Depends(get_current_user)) -> float:
    """
    Get net-worth from portfolio (holdings value and cash) at current_ts field in portfolio.
    """
    portfolio = await Portfolio.find_one(Portfolio.user_id == current_user_id, Portfolio.id == portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    net_worth = portfolio.cash_remaining
    for holding in portfolio.holdings:
        latest_price = await TickData.find_one(TickData.stock_symbol == holding.stock_symbol, TickData.timestamp <= portfolio.current_ts, sort=TickData.timestamp.desc())
        if latest_price:
            net_worth += holding.quantity * latest_price.price

    return net_worth
