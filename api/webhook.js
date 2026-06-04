export default async function handler(req, res) {
  // Chartink se jo bhi aaya usko GitHub ke format me badal do
  const body = {
    event_type: "Volume_missmatch", // Ye hardcode kar diya
    client_payload: {
      stocks: req.body.stocks || "Test",
      trigger_prices: req.body.trigger_prices || ""
    }
  };

  // Ab GitHub ko bhej do
  await fetch('https://api.github.com/repos/zenova2211/zenova_stocks/dispatches', {
    method: 'POST',
    headers: {
      'Authorization': `token ${process.env.GH_TOKEN}`,
      'Accept': 'application/vnd.github.everest-preview+json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  res.status(200).json({ ok: true });
}
