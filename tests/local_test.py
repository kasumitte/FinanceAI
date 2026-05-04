from unittest.mock import AsyncMock, patch
import pytest
from src.categorizer import get_AIResponse
from src.importer import import_transactions
from src.charts import generate_category_chart


# ------ LLM API ------
@pytest.mark.asyncio
@patch("src.categorizer.get_transactions_withoutCat")
@patch("src.categorizer.update_TransactionCategory")
async def test_AI_connection(mock_update, mock_get):
    ClientMock = AsyncMock()
    mock_pool = AsyncMock()
    
    mock_get.return_value = [
        {"name": "food", "amount": 1000},
        {"name": "transport", "amount": 1500}
    ] 
    ClientMock.chat.completions.create.return_value.choices[0].message.content = '[{"transaction_id": 1, "category": "food"}]'
    
    await get_AIResponse(client=ClientMock, conn_pool=mock_pool)
    
    # Test if "update_TransactionCategory" was called at least one time
    assert mock_update.called
    
@pytest.mark.asyncio
@patch("src.categorizer.get_transactions_withoutCat")
async def test_no_info_was_given(mock_get):
    ClientMock = AsyncMock()
    
    mock_get.return_value = [
        {"name": "food", "amount": 1000},
        {"name": "transport", "amount": 1500}
    ] 
    
    ClientMock.chat.completions.create.side_effect = ValueError("Empty response from AI")
    # Test for empty response
    with pytest.raises(ValueError, match="Empty response from AI"):
        await get_AIResponse(client=ClientMock, conn_pool=mock_get)

    
# ------ IMPORTER ------
@pytest.mark.asyncio
@patch("src.importer.save_transaction")
async def test_import_function(mock_func, tmp_path):
    given_file = tmp_path / "testing.csv"
    given_file.write_text("date,description,amount\n2026-01-01,test,100")
    
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = AsyncMock() 
    
    await import_transactions(conn_pool=mock_pool, filepath=given_file)
    
    assert mock_func.called
    
# ------ CHARTS ------
@pytest.mark.asyncio
@patch("src.charts.get_category_breakdown")
async def test_charts_generation(mock_breakdown, tmp_path):
    gen_path = tmp_path / "graphs"
    gen_path.mkdir(parents=True, exist_ok=True)
    
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = AsyncMock() 
    
    mock_breakdown.return_value = [
        {"name": "food", "amount": 1000},
        {"name": "transport", "amount": 1500}
    ]
    
    result = await generate_category_chart(conn_pool=mock_pool, output_path=gen_path)
    
    assert result is True
    