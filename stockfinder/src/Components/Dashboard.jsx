import { useEffect, useState } from "react";
import API from "../services/api";

function Dashboard() {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    loadStocks();
  }, []);

  const loadStocks = async () => {
    try {
      const res = await API.get("/candidates");
      setStocks(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <h1>Breakout Scanner</h1>

      <table border="1">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>Score</th>
            <th>Volume Ratio</th>
          </tr>
        </thead>

        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.symbol}>
              <td>{stock.symbol}</td>
              <td>{stock.price}</td>
              <td>{stock.score}</td>
              <td>{stock.vol_ratio}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Dashboard;