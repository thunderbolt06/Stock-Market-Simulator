from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from assessment_app.models.models import Holding, Portfolio, TickData, Trade
from assessment_app.service.auth_service import get_current_user

router = APIRouter()


@router.post("/market/data/tick", response_model=TickData)
async def get_market_data_tick(stock_symbol: str, current_ts: datetime, current_user_id: str = Depends(get_current_user)) -> TickData:
    """
    Get data for stocks for a given datetime from `data` folder.
    Please note consider price value in TickData to be average of open and close price column value for the timestamp from the data file.
    """
    tick_data = await TickData.find_one(TickData.stock_symbol == stock_symbol, TickData.timestamp == current_ts)
    if tick_data is None:
        raise HTTPException(status_code=404, detail="No data found for given stock symbol and datetime")
    return tick_data


@router.post("/market/data/range", response_model=list[TickData])
async def get_market_data_range(stock_symbol: str, from_ts: datetime, to_ts: datetime, current_user_id: str = Depends(get_current_user)) -> list[TickData]:
    """
    Get data for stocks for a given datetime from `data` folder.
    Please note consider price value in TickData to be average of open and close price column value for the timestamp from the data file.
    """
    tick_data = await TickData.find(TickData.stock_symbol == stock_symbol, TickData.timestamp >= from_ts, TickData.timestamp <= to_ts).sort(TickData.timestamp).to_list()
    if not tick_data:
        raise HTTPException(status_code=404, detail="No data found for given stock symbol and datetime range")
    return tick_data


@router.post("/market/trade", response_model=Trade)
async def trade_stock(trade: Trade, current_user_id: str = Depends(get_current_user)) -> Trade:
    """
    Only if trade.price is within Open and Close price of that stock on the execution timestamp, then trade should be successful.
    Trade.price must be average of Open and Close price of that stock on the execution timestamp.
    Also, update the portfolio and trade history with the trade details and adjust cash and networth appropriately.
    On every trade, current_ts of portfolio also becomes today.
    One cannot place trade in date (Trade.execution_ts) older than portfolio.current_ts
    """

    # Get the portfolio for the user
    portfolio = await Portfolio.find_one(Portfolio.user_id == current_user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio found for the user")

    # Check if the trade timestamp is older than the current timestamp
    if trade.execution_ts < portfolio.current_ts:
        raise HTTPException(status_code=400, detail="Trade timestamp older than portfolio timestamp")

    # Get the tick data for the given stock on the given timestamp
    tick_data = await TickData.find_one(TickData.stock_symbol == trade.stock_symbol, TickData.timestamp == trade.execution_ts)
    if not tick_data:
        raise HTTPException(status_code=404, detail="No tick data found for the given stock on the given timestamp")

    # Check if the trade price is within the open and close price of the tick data
    if trade.price < tick_data.open_price or trade.price > tick_data.close_price:
        raise HTTPException(status_code=400, detail="Trade price is not within the open and close price of the tick data")

    # Calculate the average price of the tick data
    avg_price = (tick_data.open_price + tick_data.close_price) / 2

    # Create a new holding for the portfolio
    holding = Holding(
        stock_symbol=trade.stock_symbol,
        quantity=trade.quantity,
        average_price=avg_price
    )

    # Add the holding to the portfolio
    portfolio.holdings.append(holding)

    # Update the portfolio cash and networth
    portfolio.cash -= avg_price * trade.quantity
    portfolio.networth += avg_price * trade.quantity

    # Update the portfolio current timestamp
    portfolio.current_ts = trade.execution_ts

    # Save the portfolio
    await portfolio.save()

    # Return the trade details
    return trade
