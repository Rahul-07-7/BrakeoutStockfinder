import { useEffect, useState } from "react";
import API from "../api";

function App() {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    loadStocks();
  }, []);

  const loadStocks = async () => {
    try {
      const res = await API.get("/candidates");
      setStocks(res.data.stocks || []);
    } catch (err) {
      console.error(err);
    }
  };

   const runScan = async () => {
  await fetch("https://brakeoutstockfinder-1.onrender.com/scan");
  const data = await res.json();

  const getStatus = async () => {
  const res = await API.get("/scan-status");
  setStatus(res.data);
};

 useEffect(() => {

  getStatus();

  const interval = setInterval(
    getStatus,
    5000
  );

  return () => clearInterval(interval);

}, []);

  console.log(data);
};

  return (
    <div style={{ padding: "20px" }}>
      <h1>🔥 Breakout Scanner</h1>
      <button onClick={runScan}>
       Run Scan
      </button>

      <h3>
  Status:
  {status.running ? " 🔄 Scanning" : " ✅ Idle"}
</h3>

<p>
  Last Scan: {status.last_scan}
</p>

<p>
  {status.message}
</p>
      {stocks.map((stock, index) => (
        <div
          key={index}
          style={{
            border: "1px solid #ddd",
            padding: "10px",
            marginBottom: "10px"
          }}
        >
          <h3>{stock.symbol}</h3>
          <p>Price: ₹{stock.price}</p>
          <p>Score: {stock.score}</p>
          <p>Volume Ratio: {stock.vol_ratio}</p>
        </div>
      ))}
    </div>
  );
}

export default App;