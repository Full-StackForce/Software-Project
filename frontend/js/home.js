        const CHALLENGES_LOCKED = false;
        const { API_BASE, session, storage } = window.PulseApp;

        // Authentication Check - Redirect to login if not authenticated
        const currentUserId = session.requireUser('/login');
        const currentUserName = storage.get(session.keys.userName, '');
        const currentUserEmail = storage.get(session.keys.userEmail, '');
        const currentUserStreak = Number(storage.get(session.keys.userStreak, 0) || 0);

        if (!currentUserId) {
            throw new Error('User session is required to load home page.');
        }
        
        // Core Wellness Tracker Workspace State Storage
        const state = {
            waterIntake: 1.2,
            waterTarget: 2.5,
            sleepHours: 8.0,
            sleepTarget: 8.0,
            pulseScore: 70,
            workouts: [],
            habits: [],
            achievements: [
                { id: 'a1', name: 'First Burn', desc: 'Logged your first fitness workout block.', unlocked: true, metric: 'Workout' },
                { id: 'a2', name: 'Water Sentinel', desc: 'Hydrate beyond 1.5L in one work interval.', unlocked: false, metric: 'Hydration' },
                { id: 'a3', name: 'Zen Master', desc: 'Maintain perfect Mindfulness habit consistency.', unlocked: true, metric: 'Habit' },
                { id: 'a4', name: 'Circadian Champion', desc: 'Match your target sleep wake parameters.', unlocked: false, metric: 'Sleep' }
            ]
        };

        // ==================== API CLIENT FUNCTIONS ====================
        
        // Fetch all workouts from backend
        async function fetchWorkouts() {
            try {
                const response = await fetch(`${API_BASE}/workouts/user/${currentUserId}`);
                if (response.ok) {
                    state.workouts = await response.json();
                    renderWorkoutHistory();
                    updatePulseScore();
                } else {
                    console.error('Failed to fetch workouts:', response.status);
                }
            } catch (error) {
                console.error('Error fetching workouts:', error);
                triggerNotification("Connection Error", "Unable to connect to backend");
            }
        }

        async function loadActiveUserName() {
            const fallbackName = currentUserName || currentUserEmail || 'Unknown User';
            const userDisplayName = document.getElementById('userDisplayName');
            const streakCounter = document.getElementById('streakCounter');

            userDisplayName.textContent = fallbackName;
            streakCounter.textContent = `${currentUserStreak} ${currentUserStreak === 1 ? 'Day' : 'Days'}`;

            try {
                const response = await fetch(`${API_BASE}/auth/me/${currentUserId}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch user details: ${response.status}`);
                }

                const user = await response.json();
                const displayName = user.name || user.email || fallbackName;
                const streakDays = Number(user.current_streak || 0);

                userDisplayName.textContent = displayName;
                streakCounter.textContent = `${streakDays} ${streakDays === 1 ? 'Day' : 'Days'}`;
                if (user.name) {
                    storage.set(session.keys.userName, user.name);
                }
                if (user.email) {
                    storage.set(session.keys.userEmail, user.email);
                }
                storage.set(session.keys.userStreak, streakDays);
            } catch (error) {
                console.error('Failed to load active user details:', error);
            }
        }

        function findHabitBySlug(slug) {
            return state.habits.find(habit => habit.slug === slug) || null;
        }

        function findSleepHabit() {
            return state.habits.find(isSleepHabitData) || null;
        }

        function isSleepHabitData(habit) {
            const slug = (habit.slug || '').toLowerCase().trim();
            const name = (habit.name || '').toLowerCase().trim();
            const category = (habit.category || '').toLowerCase().trim();
            const targetValue = Number(habit.target_value ?? habit.targetValue ?? 0);

            if (slug.includes('sleep') || name.includes('sleep')) {
                return true;
            }

            return category === 'recovery' && targetValue >= 5 && targetValue <= 12;
        }

        function normalizeSleepDurationValue(value) {
            const numericValue = Number(value || 0);
            return numericValue > 24 ? Number((numericValue / 60).toFixed(1)) : Number(value || 0);
        }

        function normalizeHabitFromApi(habit) {
            const unit = (habit.unit || '').toLowerCase().trim();
            const hasMinuteUnit = ['minute', 'minutes', 'min', 'mins'].includes(unit);
            const sleepLikeHabit = isSleepHabitData(habit);
            const normalizeAsSleepDuration = sleepLikeHabit || hasMinuteUnit;

            return {
                id: habit.id,
                name: habit.name,
                slug: habit.slug,
                type: normalizeAsSleepDuration ? 'duration' : habit.track_method,
                value: normalizeAsSleepDuration ? normalizeSleepDurationValue(habit.current_value) : habit.current_value,
                targetValue: normalizeAsSleepDuration ? normalizeSleepDurationValue(habit.target_value) : habit.target_value,
                unit: normalizeAsSleepDuration ? 'hours' : habit.unit,
                category: habit.category,
                streak_count: habit.streak_count,
                completed_today: habit.completed_today,
                user_id: habit.user_id
            };
        }

        function syncCoreMetricsFromHabits() {
            const hydrationHabit = findHabitBySlug('hydration');
            if (hydrationHabit) {
                state.waterIntake = hydrationHabit.value;
                state.waterTarget = hydrationHabit.targetValue;
            }

            const sleepHabit = findSleepHabit();
            if (sleepHabit) {
                state.sleepHours = sleepHabit.value;
                state.sleepTarget = sleepHabit.targetValue;
            }
        }

        async function logHabitProgressOnBackend(habitId, payload) {
            try {
                const response = await fetch(`${API_BASE}/habits/${habitId}/log`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`Failed to log habit progress: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('Failed to log habit progress:', error);
                return null;
            }
        }

        function renderHydrationState() {
            const progressPercent = Math.min(Math.round((state.waterIntake / state.waterTarget) * 100), 100);

            waterGlassPercent.textContent = `${progressPercent}%`;
            waterFluidLevel.style.height = `${progressPercent}%`;
            dashWaterText.innerHTML = `${state.waterIntake.toFixed(1)} <span class="text-xs font-normal text-gray-500 font-mono">of ${state.waterTarget}L</span>`;
            dashWaterProgressPercent.textContent = `${progressPercent}%`;
            dashWaterProgressBar.style.width = `${progressPercent}%`;
            document.getElementById('challengeProgressWater').textContent = `${progressPercent}%`;
            document.getElementById('challengeProgressWaterBar').style.width = `${progressPercent}%`;

            if (state.waterIntake >= state.waterTarget) {
                document.getElementById('hydrationStatusCommentary').textContent = 'Weekly Target Completed! High performance cell volume.';
            } else {
                document.getElementById('hydrationStatusCommentary').textContent = `${(state.waterTarget - state.waterIntake).toFixed(1)}L remaining to optimal metabolic state.`;
            }
        }

        function renderSleepState() {
            const hours = parseFloat(state.sleepHours.toFixed(1));
            sleepSum.textContent = `${hours} hrs`;
            dashSleepText.innerHTML = `${hours} hrs <span class="text-xs font-normal text-gray-500">Duration</span>`;

            const indexVal = Math.min(Math.round((hours / state.sleepTarget) * 100), 100);
            let rating = 'Compromised';
            if (hours >= 7.5 && hours <= 9) rating = 'Excellent';
            else if (hours >= 6 && hours < 7.5) rating = 'Sufficient';
            document.getElementById('sleepQualityIndex').textContent = `${rating} (${indexVal}%)`;
        }

        // Log a new workout to backend
        async function logWorkoutToBackend(workoutData) {
            try {
                const payload = {
                    user_id: currentUserId,
                    type: workoutData.type,
                    duration_minutes: workoutData.duration,
                    calories_burned: Math.round(workoutData.duration * 6.5),
                    notes: workoutData.notes,
                    mood_level: 3
                };

                const response = await fetch(`${API_BASE}/workouts/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const newWorkout = await response.json();
                    state.workouts.unshift(newWorkout);
                    renderWorkoutHistory();
                    updatePulseScore();
                    triggerNotification("Dynamic Workout Logged", `${workoutData.type} logged successfully.`);
                } else {
                    const error = await response.json();
                    triggerNotification("Error", error.detail || "Failed to log workout");
                }
            } catch (error) {
                console.error('Error logging workout:', error);
                triggerNotification("Error", "Failed to log workout");
            }
        }

        // Fetch all habits from backend
        async function fetchHabits() {
            try {
                const response = await fetch(`${API_BASE}/habits/user/${currentUserId}`);
                if (response.ok) {
                    const apiHabits = await response.json();
                    state.habits = apiHabits.map(normalizeHabitFromApi);
                    syncCoreMetricsFromHabits();
                    renderHydrationState();
                    renderSleepState();
                    renderDashboardChecklist();
                    renderHabitsInventory();
                    updatePulseScore();
                } else {
                    console.error('Failed to fetch habits:', response.status);
                }
            } catch (error) {
                console.error('Error fetching habits:', error);
            }
        }

        // Create a new habit on backend
        async function createHabitOnBackend(habitData) {
            try {
                const payload = {
                    user_id: currentUserId,
                    name: habitData.name,
                    category: habitData.category || 'custom',
                    unit: habitData.unit || 'count',
                    track_method: habitData.type || 'numeric',
                    frequency: habitData.frequency || 'daily',
                    target_value: habitData.targetValue || 1
                };

                const response = await fetch(`${API_BASE}/habits/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const newHabit = await response.json();
                    state.habits.push({
                        id: newHabit.id,
                        name: newHabit.name,
                        slug: newHabit.slug,
                        type: newHabit.track_method,
                        value: 0,
                        targetValue: newHabit.target_value,
                        unit: newHabit.unit,
                        category: newHabit.category,
                        streak_count: 0,
                        completed_today: false,
                        user_id: newHabit.user_id
                    });
                    renderHabitsInventory();
                    renderDashboardChecklist();
                    updatePulseScore();
                    triggerNotification("Habit Engineered", "Successfully logged and deployed to daily workspaces.");
                } else {
                    const error = await response.json();
                    triggerNotification("Error", error.detail || "Failed to create habit");
                }
            } catch (error) {
                console.error('Error creating habit:', error);
                triggerNotification("Error", "Failed to create habit");
            }
        }

        // Update habit completion status on backend
        async function updateHabitOnBackend(habitId, payload) {
            try {
                const response = await fetch(`${API_BASE}/habits/${habitId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    await fetchHabits();
                    updatePulseScore();
                } else {
                    console.error('Failed to update habit:', response.status);
                }
            } catch (error) {
                console.error('Error updating habit:', error);
            }
        }

        // Fetch dashboard summary
        async function fetchDashboardSummary() {
            try {
                const response = await fetch(`${API_BASE}/dashboard/user/${currentUserId}`);
                if (response.ok) {
                    const summary = await response.json();
                    console.log('Dashboard summary:', summary);
                } else {
                    console.error('Failed to fetch dashboard:', response.status);
                }
            } catch (error) {
                console.error('Error fetching dashboard:', error);
            }
        }

        // ==================== END API CLIENT FUNCTIONS ====================

        // Logout Function
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                storage.removeMany([
                    session.keys.userId,
                    session.keys.userName,
                    session.keys.userEmail,
                    session.keys.userStreak,
                ]);
                window.location.href = 'http://127.0.0.1:8000/login';
            }
        }

        // Cache DOM elements
        const waterGlassPercent = document.getElementById('waterGlassPercent');
        const waterFluidLevel = document.getElementById('waterFluidLevel');
        const dashWaterText = document.getElementById('dashWaterText');
        const dashWaterProgressPercent = document.getElementById('dashWaterProgressPercent');
        const dashWaterProgressBar = document.getElementById('dashWaterProgressBar');

        const bedtimeInput = document.getElementById('bedtimeInput');
        const waketimeInput = document.getElementById('waketimeInput');
        const sleepSum = document.getElementById('sleepSum');
        const dashSleepText = document.getElementById('dashSleepText');

        const dashActiveDaysCount = document.getElementById('dashActiveDaysCount');
        const dashActiveDaysProgressContainer = document.getElementById('dashActiveDaysProgressContainer');
        const peakActiveDisplay = document.getElementById('peakActiveDisplay');

        const dashHabitText = document.getElementById('dashHabitText');
        const dashHabitsStatus = document.getElementById('dashHabitsStatus');

        const dashPulseScore = document.getElementById('dashPulseScore');
        const dashPulseRing = document.getElementById('dashPulseRing');

        const chartArea = document.getElementById('chartArea');
        const chartLine = document.getElementById('chartLine');
        const liveChartIndicator = document.getElementById('liveChartIndicator');
        const chartProjectionLine = document.getElementById('chartProjectionLine');
        const chartProjectedLabel = document.getElementById('chartProjectedLabel');
        const chartActualPoints = document.getElementById('chartActualPoints');

        function formatDurationValue(value, isHourBased) {
            if (isHourBased) {
                return Number(value || 0).toFixed(1);
            }
            return `${Math.round(Number(value || 0))}`;
        }

        function toChartX(minutesIntoDay) {
            return Math.max(0, Math.min(500, (minutesIntoDay / 1440) * 500));
        }

        function toChartY(minutes, maxMinutes) {
            const top = 15;
            const bottom = 140;
            const safeMax = Math.max(maxMinutes, 1);
            const ratio = Math.max(0, Math.min(1, minutes / safeMax));
            return bottom - ratio * (bottom - top);
        }

        function renderActivityTimelineChart() {
            const todaysWorkouts = state.workouts
                .filter(workout => {
                    const timestamp = new Date(workout.completed_at);
                    return timestamp.toDateString() === new Date().toDateString();
                })
                .sort((a, b) => new Date(a.completed_at) - new Date(b.completed_at));

            if (todaysWorkouts.length === 0) {
                chartArea.setAttribute('d', 'M0,150 L500,150 L500,150 Z');
                chartLine.setAttribute('d', '');
                chartProjectionLine.setAttribute('d', '');
                chartActualPoints.innerHTML = '';
                liveChartIndicator.style.display = 'none';
                chartProjectedLabel.textContent = 'Projected EOD: 0 min';
                peakActiveDisplay.textContent = 'No workouts logged today';
                return;
            }

            let cumulativeMinutes = 0;
            const points = todaysWorkouts.map(workout => {
                cumulativeMinutes += Number(workout.duration_minutes || 0);
                const timestamp = new Date(workout.completed_at);
                const minutesIntoDay = timestamp.getHours() * 60 + timestamp.getMinutes();
                return { minutesIntoDay, cumulativeMinutes };
            });

            const now = new Date();
            const elapsedHours = Math.max((now.getHours() * 60 + now.getMinutes()) / 60, 1 / 6);
            const projectedEndOfDay = Math.max(
                cumulativeMinutes,
                Math.min(Math.round((cumulativeMinutes / elapsedHours) * 24), 300)
            );
            const maxMinutes = Math.max(projectedEndOfDay, cumulativeMinutes, 30);

            const linePath = points
                .map((point, index) => `${index === 0 ? 'M' : 'L'}${toChartX(point.minutesIntoDay)},${toChartY(point.cumulativeMinutes, maxMinutes)}`)
                .join(' ');
            chartLine.setAttribute('d', linePath);

            const firstPoint = points[0];
            const areaPath = `${linePath} L${toChartX(firstPoint.minutesIntoDay)},150 L${toChartX(firstPoint.minutesIntoDay)},${toChartY(firstPoint.cumulativeMinutes, maxMinutes)} Z`;
            chartArea.setAttribute('d', areaPath);

            chartActualPoints.innerHTML = points
                .map(point => `<circle cx="${toChartX(point.minutesIntoDay)}" cy="${toChartY(point.cumulativeMinutes, maxMinutes)}" r="4" fill="#131520" stroke="#6366F1" stroke-width="2.5" />`)
                .join('');

            const lastPoint = points[points.length - 1];
            const lastX = toChartX(lastPoint.minutesIntoDay);
            const lastY = toChartY(lastPoint.cumulativeMinutes, maxMinutes);
            liveChartIndicator.style.display = '';
            liveChartIndicator.setAttribute('cx', `${lastX}`);
            liveChartIndicator.setAttribute('cy', `${lastY}`);

            const projectedX = 500;
            const projectedY = toChartY(projectedEndOfDay, maxMinutes);
            chartProjectionLine.setAttribute('d', `M${lastX},${lastY} L${projectedX},${projectedY}`);
            chartProjectedLabel.textContent = `Projected EOD: ${projectedEndOfDay} min`;

            peakActiveDisplay.textContent = `Today ${cumulativeMinutes} min | Projected ${projectedEndOfDay} min`;
        }

        // Navigation Tab Switch Logic
        function switchTab(tabId) {
            if (tabId === 'challenges' && CHALLENGES_LOCKED) {
                triggerNotification('Locked', 'Challenges are temporarily disabled.');
                return;
            }

            document.querySelectorAll('.tab-content').forEach(element => {
                element.classList.add('hidden');
            });
            document.getElementById(`tab-${tabId}`).classList.remove('hidden');

            document.querySelectorAll('.pp-tab-container .pp-tab-btn').forEach(button => {
                button.className = "pp-tab-btn pp-tab-btn--inactive";
            });
            document.getElementById(`tabBtn-${tabId}`).className = "pp-tab-btn pp-tab-btn--active";
        }

        function applyInitialTabFromQuery() {
            const requestedTab = new URLSearchParams(window.location.search).get('tab');
            if (!requestedTab) {
                return;
            }

            const allowedTabs = new Set(['workspace', 'workouts', 'habits', 'challenges']);
            if (allowedTabs.has(requestedTab)) {
                switchTab(requestedTab);
            }
        }

        // Complex Multi-factor Daily Score Equation
        function updatePulseScore() {
            const hydRatio = Math.min(state.waterIntake / state.waterTarget, 1.0);
            const sleepRatio = Math.min(state.sleepHours / state.sleepTarget, 1.0);
            const workoutCountRatio = Math.min(state.workouts.length / 3, 1.0);
            
            let habitsTotalCount = state.habits.length;
            let habitsPassedCount = 0;
            state.habits.forEach(h => {
                if (h.type === 'checkbox' && h.value === true) {
                    habitsPassedCount++;
                } else if (h.type === 'numeric' && h.value >= h.targetValue) {
                    habitsPassedCount++;
                } else if (h.type === 'duration' && h.value >= h.targetValue) {
                    habitsPassedCount++;
                }
            });
            const habitRatio = habitsTotalCount > 0 ? (habitsPassedCount / habitsTotalCount) : 0;

            const finalScore = Math.round(
                (hydRatio * 25) + (sleepRatio * 25) + (workoutCountRatio * 25) + (habitRatio * 25)
            );

            state.pulseScore = finalScore;
            dashPulseScore.textContent = `${finalScore}%`;

            const circumference = 339.29;
            const offset = circumference - (finalScore / 100) * circumference;
            dashPulseRing.setAttribute('stroke-dashoffset', offset);

            const circadianStats = document.getElementById('circadianStats');
            if (state.sleepHours >= 7.5 && state.sleepHours <= 9) {
                circadianStats.textContent = "Aligned (Optimal)";
                circadianStats.className = "text-pulseGreen font-bold font-mono";
            } else if (state.sleepHours < 6.5) {
                circadianStats.textContent = "Deficit Tracked";
                circadianStats.className = "text-amber-500 font-bold font-mono";
            } else {
                circadianStats.textContent = "Extended / Over";
                circadianStats.className = "text-neonBlue font-bold font-mono";
            }

            const habitPercent = habitsTotalCount > 0 ? Math.round((habitsPassedCount / habitsTotalCount) * 100) : 0;
            dashHabitText.innerHTML = `${habitPercent}% <span class="text-xs font-normal text-gray-500">Today</span>`;
            dashHabitsStatus.textContent = `${habitsPassedCount}/${habitsTotalCount} Completed`;

            document.getElementById('challengeProgressHabit').textContent = `${habitsPassedCount} / ${habitsTotalCount}`;
            const challengeHabitBar = document.getElementById('challengeProgressHabitBar');
            challengeHabitBar.style.width = habitsTotalCount > 0 ? `${(habitsPassedCount / habitsTotalCount) * 100}%` : '0%';

            evaluateBadgesAchievements();
        }

        // Hydration Tracker Operations
        async function addWater(amountMl) {
            const addedLiters = amountMl / 1000;
            const hydrationHabit = findHabitBySlug('hydration');
            if (!hydrationHabit) {
                triggerNotification("Hydration Missing", "Hydration habit is not available yet.");
                return;
            }

            const updatedHabit = await logHabitProgressOnBackend(hydrationHabit.id, { amount: addedLiters });
            if (!updatedHabit) {
                triggerNotification("Error", "Failed to log hydration.");
                return;
            }

            hydrationHabit.value = updatedHabit.current_value;
            hydrationHabit.targetValue = updatedHabit.target_value;
            hydrationHabit.completed_today = updatedHabit.completed_today;
            state.waterIntake = parseFloat(updatedHabit.current_value.toFixed(2));
            state.waterTarget = updatedHabit.target_value;
            renderHydrationState();

            updatePulseScore();
            triggerNotification("Hydration Logged", `Injected ${amountMl}ml clean hydration to systems.`);
        }

        async function resetWater() {
            const hydrationHabit = findHabitBySlug('hydration');
            if (!hydrationHabit) {
                return;
            }

            const updatedHabit = await logHabitProgressOnBackend(hydrationHabit.id, { value: 0, completed_today: false });
            if (!updatedHabit) {
                return;
            }

            hydrationHabit.value = updatedHabit.current_value;
            hydrationHabit.completed_today = updatedHabit.completed_today;
            state.waterIntake = 0.0;
            renderHydrationState();

            updatePulseScore();
        }

        // Calculate sleep intervals
        async function calculateSleep(options = {}) {
            const { persist = true, silent = false } = options;
            const bedtimeVal = bedtimeInput.value;
            const waketimeVal = waketimeInput.value;

            if (!bedtimeVal || !waketimeVal) return;

            const [startH, startM] = bedtimeVal.split(':').map(Number);
            const [endH, endM] = waketimeVal.split(':').map(Number);

            let diffMinutes = (endH * 60 + endM) - (startH * 60 + startM);
            if (diffMinutes < 0) {
                diffMinutes += 24 * 60;
            }

            const hours = parseFloat((diffMinutes / 60).toFixed(1));
            const sleepHabit = findHabitBySlug('sleep');
            if (sleepHabit && persist) {
                const updatedHabit = await logHabitProgressOnBackend(sleepHabit.id, { value: hours });
                if (updatedHabit) {
                    sleepHabit.value = updatedHabit.current_value;
                    sleepHabit.targetValue = updatedHabit.target_value;
                    sleepHabit.completed_today = updatedHabit.completed_today;
                    state.sleepHours = updatedHabit.current_value;
                    state.sleepTarget = updatedHabit.target_value;
                } else {
                    state.sleepHours = hours;
                }
            } else {
                state.sleepHours = hours;
            }
            renderSleepState();

            updatePulseScore();
            if (!silent) {
                triggerNotification("Circadian Balance Tracked", `Logged sleep duration at ${hours} hours.`);
            }
        }

        // Dynamic Habits Inventory Renderer
        function renderHabitsInventory() {
            const container = document.getElementById('customHabitsInventory');
            container.innerHTML = '';

            state.habits.forEach((habit, idx) => {
                const card = document.createElement('div');
                card.className = "bg-darkBg border border-panelBorder/80 rounded-2xl p-4 flex flex-col justify-between space-y-4";
                
                let valDisplay = "";
                if (habit.type === 'checkbox') {
                    valDisplay = habit.value ? "Completed" : "Pending";
                } else if (habit.type === 'numeric') {
                    valDisplay = `${habit.value} / ${habit.targetValue} ${habit.unit}`;
                } else if (habit.type === 'duration') {
                    valDisplay = `${formatDurationValue(habit.value, true)} / ${formatDurationValue(habit.targetValue, true)} hrs`;
                }

                card.innerHTML = `
                    <div class="space-y-1">
                        <div class="flex justify-between items-start">
                            <span class="text-[9px] font-bold text-indigo-400 uppercase tracking-widest font-mono">${habit.category}</span>
                            ${habit.slug === 'hydration' || habit.slug === 'sleep' || habit.slug === 'workout' ? '' : '<button onclick="deleteHabit(' + idx + ')" class="text-gray-500 hover:text-red-400 text-xs font-bold hover:scale-105 transition-all">Delete</button>'}
                        </div>
                        <h4 class="text-sm font-bold text-white">${habit.name}</h4>
                    </div>
                    <div class="flex justify-between items-center bg-panelBg/60 p-2.5 rounded-xl border border-panelBorder/40">
                        <span class="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Value:</span>
                        <span class="text-xs font-mono font-bold text-indigo-300">${valDisplay}</span>
                    </div>
                `;
                container.appendChild(card);
            });

            updatePulseScore();
        }

        // Dynamic Active Dashboard Habits List Checker
        function renderDashboardChecklist() {
            const container = document.getElementById('dynamicChecklistContainer');
            container.innerHTML = '';

            if (state.habits.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-6 border border-dashed border-panelBorder rounded-xl">
                        <span class="text-xs text-gray-500">No habits set. Switch to Habit Builder tab to launch custom targets.</span>
                    </div>
                `;
                return;
            }

            state.habits.forEach((habit, idx) => {
                const div = document.createElement('div');
                div.className = "flex flex-col sm:flex-row items-stretch sm:items-center justify-between p-3 rounded-xl bg-panelBg/80 border border-panelBorder/60 hover:bg-panelBg transition-all gap-3";

                if (habit.type === 'checkbox') {
                    div.innerHTML = `
                        <div class="flex flex-col">
                            <span class="text-xs font-medium text-gray-300">${habit.name}</span>
                            <span class="text-[9px] uppercase font-bold text-indigo-400 tracking-wider">${habit.category}</span>
                        </div>
                        <div class="flex items-center gap-2 self-end sm:self-auto">
                            <span class="text-[10px] text-gray-500 font-mono">${habit.value ? "Complete" : "Pending"}</span>
                            <input type="checkbox" onchange="toggleCheckboxHabit(${idx})" ${habit.value ? 'checked' : ''} class="rounded border-gray-700 text-brandPurple focus:ring-brandPurple/40 w-5 h-5 bg-darkBg cursor-pointer">
                        </div>
                    `;
                } else if (habit.type === 'numeric') {
                    div.innerHTML = `
                        <div class="flex flex-col">
                            <span class="text-xs font-medium text-gray-300">${habit.name}</span>
                            <span class="text-[9px] uppercase font-bold text-indigo-400 tracking-wider">${habit.category} (${habit.unit})</span>
                        </div>
                        <div class="flex items-center gap-3 self-end sm:self-auto">
                            <span class="text-[11px] font-mono text-gray-300 font-bold">${habit.value}/${habit.targetValue}</span>
                            <div class="flex gap-1.5">
                                <button onclick="incrementHabitValue(${idx}, -1)" class="w-6 h-6 rounded bg-darkBg border border-panelBorder text-xs hover:text-white transition-all flex items-center justify-center">-</button>
                                <button onclick="incrementHabitValue(${idx}, 1)" class="w-6 h-6 rounded bg-darkBg border border-panelBorder text-xs hover:text-white transition-all flex items-center justify-center">+</button>
                            </div>
                        </div>
                    `;
                } else if (habit.type === 'duration') {
                    const durationLabel = 'Hours';
                    const durationUnit = 'hrs';
                    const durationStep = 0.5;
                    div.innerHTML = `
                        <div class="flex flex-col">
                            <span class="text-xs font-medium text-gray-300">${habit.name}</span>
                            <span class="text-[9px] uppercase font-bold text-indigo-400 tracking-wider">${habit.category} (${durationLabel})</span>
                        </div>
                        <div class="flex items-center gap-3 self-end sm:self-auto">
                            <span class="text-[11px] font-mono text-gray-300 font-bold">${formatDurationValue(habit.value, true)}/${formatDurationValue(habit.targetValue, true)} ${durationUnit}</span>
                            <div class="flex gap-1.5">
                                <button onclick="incrementHabitValue(${idx}, ${-durationStep})" class="w-6 h-6 rounded bg-darkBg border border-panelBorder text-xs hover:text-white transition-all flex items-center justify-center">-</button>
                                <button onclick="incrementHabitValue(${idx}, ${durationStep})" class="w-6 h-6 rounded bg-darkBg border border-panelBorder text-xs hover:text-white transition-all flex items-center justify-center">+</button>
                            </div>
                        </div>
                    `;
                }

                container.appendChild(div);
            });
        }

        // Toggle configuration visibility targets
        function toggleHabitTargetOptions() {
            const type = document.getElementById('habitTrackMethod').value;
            const targetWrapper = document.getElementById('habitTargetValueWrapper');
            const unitInput = document.getElementById('habitUnit');

            if (type === 'checkbox') {
                targetWrapper.classList.add('hidden');
            } else if (type === 'numeric') {
                targetWrapper.classList.remove('hidden');
                unitInput.placeholder = "e.g. Cups";
                unitInput.value = "Cups";
            } else if (type === 'duration') {
                targetWrapper.classList.remove('hidden');
                unitInput.placeholder = "Minutes";
                unitInput.value = "Minutes";
                unitInput.readOnly = true;
            }
        }

        // Add Custom Habit Operation
        function createNewHabit() {
            const nameInput = document.getElementById('habitNameInput');
            const typeSelect = document.getElementById('habitTrackMethod');
            const targetNum = document.getElementById('habitTargetNumber');
            const unitInput = document.getElementById('habitUnit');
            const catSelect = document.getElementById('habitCategory');

            if (!nameInput.value.trim()) {
                triggerNotification("Config Error", "Please provide a valid Habit Name.");
                return;
            }

            const habitData = {
                name: nameInput.value.trim(),
                type: typeSelect.value,
                targetValue: typeSelect.value === 'checkbox' ? 1 : parseFloat(targetNum.value),
                unit: unitInput.value || 'Units',
                frequency: 'daily',
                category: catSelect.value
            };

            createHabitOnBackend(habitData);
            
            nameInput.value = '';
            targetNum.value = '5';
        }

        // Checkbox interaction
        function toggleCheckboxHabit(idx) {
            state.habits[idx].value = !state.habits[idx].value;
            state.habits[idx].completed_today = state.habits[idx].value;
            logHabitProgressOnBackend(state.habits[idx].id, { completed_today: state.habits[idx].value });
            renderDashboardChecklist();
            renderHabitsInventory();
        }

        // Slider / Counter values
        function incrementHabitValue(idx, increment) {
            const target = state.habits[idx];
            let rawValue = target.value + increment;
            if (rawValue < 0) rawValue = 0;
            if (target.type === 'duration') {
                rawValue = Math.round(rawValue * 10) / 10;
            }
            target.value = rawValue;
            target.completed_today = rawValue >= target.targetValue;

            logHabitProgressOnBackend(target.id, { value: rawValue });
            renderDashboardChecklist();
            renderHabitsInventory();
        }

        // Delete Habits Entry
        async function deleteHabit(idx) {
            const habit = state.habits[idx];
            const response = await fetch(`${API_BASE}/habits/${habit.id}`, { method: 'DELETE' });
            if (!response.ok) {
                const error = await response.json();
                triggerNotification("Error", error.detail || "Failed to delete habit");
                return;
            }

            state.habits.splice(idx, 1);
            renderHabitsInventory();
            renderDashboardChecklist();
        }

        // Workout Tracking History Renderers
        function renderWorkoutHistory() {
            const container = document.getElementById('workoutHistoryContainer');
            container.innerHTML = '';

            state.workouts.forEach((workout, idx) => {
                const item = document.createElement('div');
                item.className = "bg-darkBg border border-panelBorder/80 rounded-2xl p-4 flex items-center justify-between gap-4 hover:border-pulseGreen/30 transition-all";
                
                let iconColor = "text-pulseGreen bg-pulseGreen/10";

                item.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="p-2.5 rounded-xl ${iconColor}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h4 class="text-sm font-bold text-white">${workout.type}</h4>
                            </div>
                            <p class="text-xs text-gray-500 mt-0.5">${workout.notes ? workout.notes : 'No session notes provided.'}</p>
                            <span class="text-[9px] font-mono text-gray-600 block mt-1">${new Date(workout.completed_at).toLocaleString()}</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-sm font-extrabold text-white font-mono block">${workout.duration_minutes}</span>
                        <span class="text-[9px] text-gray-500 uppercase tracking-widest block">Mins</span>
                    </div>
                `;
                container.appendChild(item);
            });

            dashActiveDaysCount.innerHTML = `${state.workouts.length} <span class="text-xs font-normal text-gray-500">Sessions Logged</span>`;
            
            dashActiveDaysProgressContainer.innerHTML = '';
            const totalWorkouts = state.workouts.length;
            for (let i = 1; i <= 7; i++) {
                const bar = document.createElement('div');
                bar.className = 'h-2.5 flex-grow rounded-md transition-all duration-300';
                if (i <= totalWorkouts) {
                    bar.className += ' bg-gradient-to-r from-pulseGreen to-emerald-400';
                } else {
                    bar.className += ' bg-gray-800';
                }
                dashActiveDaysProgressContainer.appendChild(bar);
            }

            let totalMins = 0;
            state.workouts.forEach(w => totalMins += w.duration_minutes);

            document.getElementById('challengeProgressFitness').textContent = `${totalMins} / 100 mins`;
            const challengeFitnessBar = document.getElementById('challengeProgressFitnessBar');
            challengeFitnessBar.style.width = `${Math.min(Math.round((totalMins / 100) * 100), 100)}%`;

            renderActivityTimelineChart();

            updatePulseScore();
        }

        // Append Workout Entry Logic
        function logWorkout() {
            const selectEl = document.getElementById('workoutTypeSelect');
            const durationEl = document.getElementById('workoutDurationSlider');
            const intensityEl = document.querySelector('input[name="intensityRadio"]:checked');
            const notesEl = document.getElementById('workoutNotes');

            const workoutData = {
                type: selectEl.value,
                duration: parseInt(durationEl.value, 10),
                intensity: intensityEl.value,
                notes: notesEl.value.trim()
            };

            logWorkoutToBackend(workoutData);
            
            notesEl.value = '';
            durationEl.value = '45';
            document.getElementById('workoutDurationLabel').textContent = '45 mins';
        }

        // Evaluate and reward achievements dynamically based on state metrics
        function evaluateBadgesAchievements() {
            if (state.waterIntake >= 1.5) {
                state.achievements[1].unlocked = true;
            }
            if (state.sleepHours >= 7.5 && state.sleepHours <= 9.0) {
                state.achievements[3].unlocked = true;
            }

            renderAchievementsGrid();
        }

        function renderAchievementsGrid() {
            const container = document.getElementById('achievementsGridContainer');
            container.innerHTML = '';

            state.achievements.forEach(ach => {
                const card = document.createElement('div');
                
                let cardClass = "pp-card pp-card-amber text-center flex flex-col items-center justify-between space-y-4 hover:scale-[1.02]";
                let iconWrapperClass = "";
                let indicatorTag = "";
                let svgBadgeMarkup = "";

                if (ach.unlocked) {
                    cardClass += " border-indigo-400/20 shadow-[0_0_20px_rgba(99,102,241,0.06)]";
                    iconWrapperClass = "w-16 h-16 rounded-full bg-indigo-500/10 border border-indigo-400/40 flex items-center justify-center relative";
                    indicatorTag = `<span class="text-[9px] uppercase tracking-wider text-pulseGreen font-bold font-mono">Unlocked</span>`;
                    
                    svgBadgeMarkup = `
                        <svg class="w-8 h-8 text-indigo-300 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
                        </svg>
                    `;
                } else {
                    cardClass += " opacity-60";
                    iconWrapperClass = "w-16 h-16 rounded-full bg-panelBg border border-dashed border-gray-700 flex items-center justify-center relative";
                    indicatorTag = `<span class="text-[9px] uppercase tracking-wider text-gray-500 font-bold font-mono">Locked</span>`;
                    
                    svgBadgeMarkup = `
                        <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                        </svg>
                    `;
                }

                card.className = cardClass;
                card.innerHTML = `
                    <div class="${iconWrapperClass}">
                        ${svgBadgeMarkup}
                    </div>
                    <div class="space-y-1">
                        <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono">${ach.name}</h4>
                        <p class="text-[11px] text-gray-400 leading-normal">${ach.desc}</p>
                    </div>
                    ${indicatorTag}
                `;
                container.appendChild(card);
            });
        }

        // Unified workspace alert engine
        function triggerNotification(title, message) {
            const toast = document.getElementById('toast');
            const titleEl = document.getElementById('toastTitle');
            const messageEl = document.getElementById('toastMessage');

            titleEl.textContent = title;
            messageEl.textContent = message;

            toast.classList.add('pp-toast--visible');

            setTimeout(() => {
                toast.classList.remove('pp-toast--visible');
            }, 3500);
        }

        // Set current date
        function updateDateDisplay() {
            const options = { month: 'long', day: 'numeric' };
            const today = new Date().toLocaleDateString('en-US', options);
            document.getElementById('dateDisplay').textContent = `Today, ${today}`;
        }

        // Initialize elements on load
        window.onload = async function() {
            applyInitialTabFromQuery();
            updateDateDisplay();
            renderDashboardChecklist();
            renderHabitsInventory();
            renderAchievementsGrid();
            renderHydrationState();
            renderSleepState();
            updatePulseScore();

            await loadActiveUserName();
            
            // Load data from backend
            await fetchHabits();
            fetchWorkouts();
            fetchDashboardSummary();
        };
