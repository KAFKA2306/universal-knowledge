/* Progressive enhancement: cards and links remain readable without JavaScript. */
(() => {
  "use strict";
  const search = document.getElementById("search");
  const stage = document.getElementById("stage");
  const order = document.getElementById("order");
  const buttons = [...document.querySelectorAll(".domain-btn")];
  const container = document.getElementById("records");
  const cards = [...container.querySelectorAll(".record")];
  const count = document.getElementById("result-count");
  const empty = document.getElementById("empty");
  const clear = document.getElementById("clear-filters");
  const normalize = text => (text || "").normalize("NFKC").toLocaleLowerCase("ja").trim();
  let activeDomain = "all";
  function render() {
    const term = normalize(search.value);
    const category = stage.value;
    let found = [];
    for (const card of cards) {
      const pass = (activeDomain === "all" || card.dataset.domain === activeDomain)
        && (category === "all" || card.dataset.stage === category)
        && normalize(card.dataset.search).includes(term);
      card.hidden = !pass;
      if (pass) found.push(card);
    }
    if (order.value === "oldest") found.sort((a,b) =>
      (a.dataset.published || "0000").localeCompare(b.dataset.published || "0000"));
    else if (order.value === "newest") found.sort((a,b) =>
      (b.dataset.published || "0000").localeCompare(a.dataset.published || "0000"));
    else found.sort((a,b) => Number(a.dataset.index) - Number(b.dataset.index));
    for (const card of found) container.appendChild(card);
    count.textContent = `${found.length}件 / 全${cards.length}件`;
    empty.hidden = found.length !== 0;
    for (const btn of buttons) btn.setAttribute("aria-pressed", String(btn.dataset.domain === activeDomain));
    const params = new URLSearchParams();
    if (term) params.set("q", search.value.trim());
    if (activeDomain !== "all") params.set("domain", activeDomain);
    if (category !== "all") params.set("stage", category);
    if (order.value !== "default") params.set("sort", order.value);
    history.replaceState(null, "", location.pathname + (params.size ? "?" + params.toString() : "") + location.hash);
  }
  for (const btn of buttons) btn.addEventListener("click", () => { activeDomain = btn.dataset.domain; render(); });
  for (const el of [search,stage,order]) el.addEventListener(el === search ? "input" : "change", render);
  clear.addEventListener("click", () => { search.value=""; stage.value="all"; order.value="default"; activeDomain="all"; render(); search.focus(); });
  const params = new URLSearchParams(location.search);
  const wanted = params.get("domain");
  if (buttons.some(btn=>btn.dataset.domain === wanted)) activeDomain=wanted;
  if (params.get("q")) search.value=params.get("q");
  if (["all","source","candidate"].includes(params.get("stage"))) stage.value=params.get("stage");
  if (["default","newest","oldest"].includes(params.get("sort"))) order.value=params.get("sort");
  render();
})();
