const { useState, useEffect } = React;

function App() {
  const [config, setConfig] = useState(null);
  const [session, setSession] = useState(null);
  const [round, setRound] = useState(1);
  const [prices, setPrices] = useState([]);
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [payoff, setPayoff] = useState(null);

  useEffect(() => {
    fetch('/config').then(res => res.json()).then(setConfig);
  }, []);

  function start(arm) {
    fetch('/start', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({arm})
    }).then(res => res.json()).then(data => {
      setSession(data.session);
      setRound(1);
      nextRound(data.session, 1);
    });
  }

  function nextRound(sessionId=session, r=round) {
    fetch(`/round/${r}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session: sessionId})
    }).then(res => res.json()).then(data => {
      setPrices(data.prices);
      setMessage("");
      setResponse("");
      setPayoff(null);
    });
  }

  function sendPrompt() {
    fetch('/prompt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session, round, prompt: message})
    }).then(res => res.json()).then(data => {
      setResponse(data.reply);
    });
  }

  function choose(idx) {
    fetch('/choose', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session, round, choice: idx})
    }).then(res => res.json()).then(data => {
      setPayoff(data.payoff);
      const next = round + 1;
      setRound(next);
      if (next <= (config ? config.num_rounds : 0)) {
        nextRound(session, next);
      }
    });
  }

  if (!config) return React.createElement('div', null, 'Loading...');
  if (!session) {
    return React.createElement('div', null,
      React.createElement('h1', {className:'text-xl font-bold mb-2'}, 'Start Experiment'),
      config.arms.map(arm =>
        React.createElement('button', {key: arm, onClick: () => start(arm), className:'m-2 p-2 border'}, arm)
      )
    );
  }

  return React.createElement('div', null,
    React.createElement('h1', {className:'text-xl font-bold'}, `Round ${round}`),
    prices.map((p, idx) =>
      React.createElement('button', {key: idx, onClick: () => choose(idx), className:'m-2 p-2 border'}, `$${p}`)
    ),
    React.createElement('div', null,
      React.createElement('textarea', {className:'border p-2 mt-2 w-full', value: message, onChange: e => setMessage(e.target.value)}),
      React.createElement('button', {className:'m-2 p-2 border', onClick: sendPrompt}, 'Ask GPT'),
      React.createElement('pre', {className:'whitespace-pre-wrap'}, response)
    ),
    payoff !== null && React.createElement('div', {className:'mt-2'}, `Payoff: ${payoff}`)
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
