/* Saved record fields are text. Only static layout belongs in innerHTML. */
(function () {
  function setText(root, field, value) {
    root.querySelector(`[data-field="${field}"]`).textContent = value ?? "";
  }

  function habitCard(habit, onDelete) {
    const card = document.createElement("div");
    card.className = "bg-darkBg border border-panelBorder/80 rounded-2xl p-4 flex flex-col justify-between space-y-4";
    card.innerHTML = `
      <div class="space-y-1">
        <div class="flex justify-between items-start">
          <span data-field="category" class="text-[9px] font-bold text-indigo-400 uppercase tracking-widest font-mono"></span>
          <button type="button" data-action="delete" class="text-gray-500 hover:text-red-400 text-xs font-bold hover:scale-105 transition-all">Delete</button>
        </div>
        <h4 data-field="name" class="text-sm font-bold text-white"></h4>
      </div>
      <div class="flex justify-between items-center bg-panelBg/60 p-2.5 rounded-xl border border-panelBorder/40">
        <span class="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Value:</span>
        <span data-field="value" class="text-xs font-mono font-bold text-indigo-300"></span>
      </div>
    `;
    let value = `${habit.value} / ${habit.targetValue} ${habit.unit}`;
    if (habit.type === "checkbox") value = habit.value ? "Completed" : "Pending";
    if (habit.type === "duration") value = `${hours(habit.value)} / ${hours(habit.targetValue)} hrs`;
    setText(card, "category", habit.category);
    setText(card, "name", habit.name);
    setText(card, "value", value);

    const button = card.querySelector('[data-action="delete"]');
    if (["hydration", "sleep", "workout"].includes(habit.slug)) {
      button.remove();
    } else {
      button.setAttribute("aria-label", `Delete ${habit.name}`);
      button.addEventListener("click", onDelete);
    }
    return card;
  }

  function hours(value) {
    return Number(value || 0).toFixed(1);
  }

  function habitChecklistItem(habit, { onToggle, onIncrement }) {
    const row = document.createElement("div");
    row.className = "flex flex-col sm:flex-row items-stretch sm:items-center justify-between p-3 rounded-xl bg-panelBg/80 border border-panelBorder/60 hover:bg-panelBg transition-all gap-3";
    row.innerHTML = `
      <div class="flex flex-col">
        <span data-field="name" class="text-xs font-medium text-gray-300"></span>
        <span data-field="category" class="text-[9px] uppercase font-bold text-indigo-400 tracking-wider"></span>
      </div>
      <div data-controls class="flex items-center gap-3 self-end sm:self-auto"></div>
    `;
    setText(row, "name", habit.name);
    setText(row, "category", habit.category);
    const controls = row.querySelector("[data-controls]");
    if (habit.type === "checkbox") {
      controls.innerHTML = `
        <span data-field="status" class="text-[10px] text-gray-500 font-mono"></span>
        <input type="checkbox" class="rounded border-gray-700 text-brandPurple focus:ring-brandPurple/40 w-5 h-5 bg-darkBg cursor-pointer">
      `;
      setText(row, "status", habit.value ? "Complete" : "Pending");
      const checkbox = controls.querySelector("input");
      checkbox.checked = Boolean(habit.value);
      checkbox.setAttribute("aria-label", `Complete ${habit.name}`);
      checkbox.addEventListener("change", onToggle);
    } else if (["numeric", "duration"].includes(habit.type)) {
      const duration = habit.type === "duration";
      setText(row, "category", `${habit.category} (${duration ? "Hours" : habit.unit})`);
      controls.innerHTML = `
        <span data-field="value" class="text-[11px] font-mono text-gray-300 font-bold"></span>
        <div class="flex gap-1.5">
          <button type="button" data-action="decrease" class="w-6 h-6 rounded bg-darkBg border border-panelBorder text-xs hover:text-white transition-all flex items-center justify-center">-</button>
          <button type="button" data-action="increase" class="w-6 h-6 rounded bg-darkBg border border-panelBorder text-xs hover:text-white transition-all flex items-center justify-center">+</button>
        </div>
      `;
      setText(row, "value", duration
        ? `${hours(habit.value)}/${hours(habit.targetValue)} hrs`
        : `${habit.value}/${habit.targetValue}`);
      for (const [action, direction] of [["decrease", -1], ["increase", 1]]) {
        const button = controls.querySelector(`[data-action="${action}"]`);
        button.setAttribute("aria-label", `${action} ${habit.name}`);
        button.addEventListener("click", () => onIncrement(direction * (duration ? 0.5 : 1)));
      }
    }
    return row;
  }

  function workoutCard(workout) {
    const card = document.createElement("div");
    card.className = "bg-darkBg border border-panelBorder/80 rounded-2xl p-4 flex items-center justify-between gap-4 hover:border-pulseGreen/30 transition-all";
    card.innerHTML = `
      <div class="flex items-center gap-3">
        <div class="p-2.5 rounded-xl text-pulseGreen bg-pulseGreen/10">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2"><h4 data-field="type" class="text-sm font-bold text-white"></h4></div>
          <p data-field="notes" class="text-xs text-gray-500 mt-0.5"></p>
          <span data-field="date" class="text-[9px] font-mono text-gray-600 block mt-1"></span>
        </div>
      </div>
      <div class="text-right">
        <span data-field="duration" class="text-sm font-extrabold text-white font-mono block"></span>
        <span class="text-[9px] text-gray-500 uppercase tracking-widest block">Mins</span>
      </div>
    `;
    setText(card, "type", workout.type);
    setText(card, "notes", workout.notes || "No session notes provided.");
    setText(card, "date", new Date(workout.completed_at).toLocaleString());
    setText(card, "duration", workout.duration_minutes);
    return card;
  }

  window.PulseApp.renderers = { habitCard, habitChecklistItem, workoutCard };
})();
