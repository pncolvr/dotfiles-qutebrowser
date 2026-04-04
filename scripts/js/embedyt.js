fetch("https://api.invidious.io/instances.json")
  .then(res => res.json())
  .then(data => {
    const best = data.reduce((max, item) => {
      const uptime = item[1]?.monitor?.uptime ?? -1;
      return uptime > (max[1]?.monitor?.uptime ?? -1) ? item : max;
    });
    const params = new URLSearchParams(window.location.search);
    const value = params.get("v");
    window.location.replace(
      `${best[1].uri}/embed/${value}`
    );
  });
