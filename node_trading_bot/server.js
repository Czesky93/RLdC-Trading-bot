
require("dotenv").config();
const express = require("express");
const bodyParser = require("body-parser");
const binance = require("binance-api-node").default;

// Initialize app and Binance client
const app = express();
const client = binance({
  apiKey: process.env.BINANCE_API_KEY,
  apiSecret: process.env.BINANCE_SECRET_KEY,
});

app.use(bodyParser.json());

// Homepage
app.get("/", (req, res) => {
  res.send("<h1>Trading Bot is running</h1>");
});

// Fetch account info
app.get("/account", async (req, res) => {
  try {
    const accountInfo = await client.accountInfo();
    res.json(accountInfo);
  } catch (error) {
    res.status(500).json({ error: "Error fetching account information" });
  }
});

// Analyze market data
app.post("/analyze", async (req, res) => {
  try {
    const symbol = req.body.symbol || "BTCUSDT";
    const prices = await client.prices();
    const price = prices[symbol];
    res.json({ symbol, price, recommendation: "hold" });
  } catch (error) {
    res.status(500).json({ error: "Error analyzing market data" });
  }
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
