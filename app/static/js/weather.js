class WeatherWidget {
  constructor() {
    this.currentLocation = null;
    this.weatherData = null;
    this.currentHours = 24;
    this.init();
  }

  init() {
    this.requestLocation();
    this.bindEvents();
  }

  bindEvents() {
    // Refresh button
    const refreshBtn = document.getElementById("weather-refresh");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => this.refreshWeather());
    }

    // Use current location button
    const useLocationBtn = document.getElementById("use-current-location-btn");
    if (useLocationBtn) {
      useLocationBtn.addEventListener("click", () => this.requestLocation());
    }
  }

  // Get weather specific styling
  getWeatherTheme(condition, temperature) {
    const temp = parseInt(temperature);
    const weatherCondition = condition.toLowerCase();

    let theme = {
      gradient: "from-blue-500 to-blue-600",
      textColor: "text-white",
      icon: "☀️",
    };

    if (temp >= 35) {
      theme.gradient = "from-red-500 via-orange-500 to-yellow-500";
      theme.icon = "🔥";
    } else if (temp >= 25) {
      theme.gradient = "from-yellow-400 via-orange-400 to-red-400";
      theme.icon = "☀️";
    } else if (temp >= 15) {
      theme.gradient = "from-blue-400 via-cyan-400 to-teal-400";
      theme.icon = "🌤️";
    } else if (temp >= 5) {
      theme.gradient = "from-slate-400 via-gray-500 to-slate-600";
      theme.icon = "❄️";
    } else {
      theme.gradient = "from-indigo-600 via-blue-700 to-slate-800";
      theme.icon = "🧊";
    }

    if (
      weatherCondition.includes("rain") ||
      weatherCondition.includes("drizzle")
    ) {
      theme.gradient = "from-slate-600 via-gray-600 to-blue-700";
      theme.icon = "🌧️";
    } else if (
      weatherCondition.includes("thunderstorm") ||
      weatherCondition.includes("storm")
    ) {
      theme.gradient = "from-slate-800 via-gray-800 to-indigo-900";
      theme.icon = "⛈️";
    } else if (weatherCondition.includes("snow")) {
      theme.gradient = "from-slate-200 via-gray-300 to-slate-400";
      theme.icon = "🌨️";
      theme.textColor = "text-gray-800";
    } else if (
      weatherCondition.includes("mist") ||
      weatherCondition.includes("fog")
    ) {
      theme.gradient = "from-gray-400 via-slate-400 to-gray-500";
      theme.icon = "🌫️";
    } else if (weatherCondition.includes("cloud")) {
      theme.gradient = "from-gray-500 via-slate-500 to-gray-600";
      theme.icon = "☁️";
    }

    return theme;
  }

  requestLocation() {
    if (!navigator.geolocation) {
      console.log("Geolocation is not supported by this browser.");
      this.loadDefaultWeather();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        this.currentLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        this.loadWeather();
      },
      (error) => {
        console.log("Error getting location:", error.message);
        this.loadDefaultWeather();
      }
    );
  }

  async loadWeather() {
    try {
      console.log("Loading weather for:", this.currentLocation);
      this.showLoading();
      this.hideError();

      let url = "/api/weather/current";
      if (this.currentLocation) {
        url += `?lat=${this.currentLocation.latitude}&lon=${this.currentLocation.longitude}`;
      }

      console.log("Fetching weather from:", url);
      const response = await fetch(url);
      const result = await response.json();

      console.log("Weather API response:", result);

      if (result.success) {
        this.weatherData = result.data;
        this.displayWeather();
        console.log("Weather updated successfully");
      } else {
        console.error("Weather API error:", result.message);
        this.showError(result.message);
      }
    } catch (error) {
      console.error("Error loading weather:", error);
      this.showError("Failed to load weather data");
    } finally {
      this.hideLoading();
    }
  }

  async loadDefaultWeather() {
    try {
      this.showLoading();

      const response = await fetch("/api/weather/current");
      const result = await response.json();

      if (result.success) {
        this.weatherData = result.data;
        this.displayWeather();
      } else {
        this.showError(result.message);
      }
    } catch (error) {
      console.error("Error loading default weather:", error);
      this.showError("Failed to load weather data");
    } finally {
      this.hideLoading();
    }
  }

  displayWeather() {
    if (!this.weatherData) {
      console.error("No weather data to display");
      return;
    }

    console.log("Displaying weather data:", this.weatherData);

    const current = this.weatherData.current;
    const daily = this.weatherData.daily;

    this.updateCurrentWeather(current);
    this.updateForecast(daily);
    this.loadHourlyForecast();

    // Get location name through reverse geocoding and notify favorites manager
    if (this.currentLocation) {
      this.getLocationNameAndNotifyFavorites();
    }
  }

  async getLocationNameAndNotifyFavorites() {
    try {
      const { latitude, longitude } = this.currentLocation;
      const response = await fetch(
        `/api/weather/location/reverse?lat=${latitude}&lon=${longitude}`
      );
      const result = await response.json();

      let locationName = "Unknown Location";
      let country = "";
      let state = "";

      if (result.success && result.data) {
        locationName =
          result.data.name || result.data.city || "Unknown Location";
        country = result.data.country || "";
        state = result.data.state || "";
      }

      // Notify favorites manager about weather update with proper location info
      if (window.updateWeatherLocationForFavorites) {
        window.updateWeatherLocationForFavorites({
          latitude: latitude,
          longitude: longitude,
          location_name: locationName,
          country: country,
          state: state,
        });
      }
    } catch (error) {
      console.error("Error getting location name:", error);
      // Fallback notification
      if (window.updateWeatherLocationForFavorites) {
        window.updateWeatherLocationForFavorites({
          latitude: this.currentLocation.latitude,
          longitude: this.currentLocation.longitude,
          location_name: "Current Location",
          country: "",
          state: "",
        });
      }
    }
  }

  updateCurrentWeather(current) {
    const container = document.getElementById("current-weather");
    if (!container) return;

    const datetime = new Date(current.datetime * 1000);
    const theme = this.getWeatherTheme(
      current.weather.description,
      current.temperature
    );

    container.innerHTML = `
      <div class="weather-card-main bg-gradient-to-br ${theme.gradient} ${
      theme.textColor
    } rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <!-- Weather Content -->
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-2xl font-bold mb-2 flex items-center">
                <span class="mr-3 text-3xl">${theme.icon}</span>
                Current Weather
              </h3>
              <p class="opacity-90 text-lg">Live conditions in your area</p>
            </div>
            <div class="text-right">
              <div class="text-sm opacity-80 mb-1">${datetime.toLocaleDateString()}</div>
              <div class="text-sm opacity-80">${datetime.toLocaleTimeString()}</div>
            </div>
          </div>

          <!-- Main Weather Display -->
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center">
              <div class="weather-icon-container mr-6 relative">
                <img src="${current.weather.icon_url}" 
                     alt="${current.weather.description}" 
                     class="w-24 h-24 drop-shadow-lg">
              </div>
              <div>
                <div class="temperature-display text-6xl font-bold mb-2">
                  ${current.temperature}°C
                </div>
                <div class="text-xl opacity-90 capitalize">
                  ${current.weather.description}
                </div>
              </div>
            </div>
            
            <!-- Weather Stats -->
            <div class="grid grid-cols-2 gap-4 text-right">
              <div class="weather-stat-item">
                <div class="text-sm opacity-80">Feels Like</div>
                <div class="text-2xl font-bold">${current.feels_like}°C</div>
              </div>
              <div class="weather-stat-item">
                <div class="text-sm opacity-80">Humidity</div>
                <div class="text-2xl font-bold">${current.humidity}%</div>
              </div>
            </div>
          </div>

          <!-- Detailed Weather Info -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6 pt-6 border-t border-white/20">
            <div class="weather-detail-card text-center p-4 rounded-xl bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-colors duration-300">
              <div class="text-3xl mb-2">🌡️</div>
              <div class="text-sm opacity-80 mb-1">Feels Like</div>
              <div class="text-xl font-bold">${current.feels_like}°C</div>
            </div>
            
            <div class="weather-detail-card text-center p-4 rounded-xl bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-colors duration-300">
              <div class="text-3xl mb-2">💧</div>
              <div class="text-sm opacity-80 mb-1">Humidity</div>
              <div class="text-xl font-bold">${current.humidity}%</div>
            </div>
            
            <div class="weather-detail-card text-center p-4 rounded-xl bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-colors duration-300">
              <div class="text-3xl mb-2">💨</div>
              <div class="text-sm opacity-80 mb-1">Wind</div>
              <div class="text-xl font-bold">${current.wind_speed} m/s</div>
            </div>
            
            <div class="weather-detail-card text-center p-4 rounded-xl bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-colors duration-300">
              <div class="text-3xl mb-2">📊</div>
              <div class="text-sm opacity-80 mb-1">Pressure</div>
              <div class="text-xl font-bold">${current.pressure} hPa</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  updateForecast(daily) {
    const container = document.getElementById("weather-forecast");
    if (!container || !daily) return;

    const forecastHTML = daily
      .slice(1, 8)
      .map((day, index) => {
        const date = new Date(day.datetime * 1000);
        const dayName = date.toLocaleDateString("en-US", { weekday: "short" });
        const dateStr = date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        });

        const theme = this.getWeatherTheme(
          day.weather.description,
          day.temp_max
        );

        return `
          <div class="forecast-card group relative bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
            <!-- Card Content -->
            <div class="relative z-10 text-center">
              <!-- Day Info -->
              <div class="mb-4">
                <div class="text-lg font-bold text-white mb-1">${dayName}</div>
                <div class="text-sm text-white/70">${dateStr}</div>
              </div>
              
              <!-- Weather Icon -->
              <div class="mb-4 relative">
                <img src="${day.weather.icon_url}" 
                     alt="${day.weather.description}" 
                     class="w-16 h-16 mx-auto drop-shadow-lg">
                <div class="absolute inset-0 rounded-full bg-gradient-to-br ${
                  theme.gradient
                } opacity-20"></div>
              </div>
              
              <!-- Weather Description -->
              <div class="text-sm text-white/90 mb-4 capitalize font-medium">
                ${day.weather.description}
              </div>
              
              <!-- Temperature Range -->
              <div class="flex justify-center items-center space-x-3 mb-4">
                <span class="text-2xl font-bold text-white">${
                  day.temp_max
                }°</span>
                <span class="text-lg text-white/60">${day.temp_min}°</span>
              </div>
              
              <!-- Additional Info -->
              <div class="flex justify-center items-center space-x-4 text-xs text-white/70">
                <div class="flex items-center">
                  <i class="fas fa-tint mr-1"></i>
                  <span>${day.humidity}%</span>
                </div>
                ${
                  day.precipitation_probability
                    ? `
                <div class="flex items-center">
                  <i class="fas fa-cloud-rain mr-1"></i>
                  <span>${day.precipitation_probability}%</span>
                </div>
                `
                    : ""
                }
              </div>
            </div>
            
            <!-- Hover effect overlay -->
            <div class="absolute inset-0 bg-gradient-to-br ${
              theme.gradient
            } opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl"></div>
          </div>
        `;
      })
      .join("");

    container.innerHTML = `
      <div class="forecast-container bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl p-8">
        <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
          <i class="fas fa-calendar-week mr-3 text-yellow-300"></i>
          7-Day Forecast
          <span class="ml-auto text-sm font-normal opacity-70">Extended outlook</span>
        </h3>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4">
          ${forecastHTML}
        </div>
      </div>
    `;
  }

  refreshWeather() {
    this.hideError();
    this.loadWeather();
  }

  showLoading() {
    const loadingElement = document.getElementById("weather-loading");
    if (loadingElement) {
      loadingElement.classList.remove("hidden");
    }
  }

  hideLoading() {
    const loadingElement = document.getElementById("weather-loading");
    if (loadingElement) {
      loadingElement.classList.add("hidden");
    }
  }

  showError(message) {
    const errorElement = document.getElementById("weather-error");
    if (errorElement) {
      errorElement.innerHTML = `
        <div class="error-card p-6 rounded-2xl text-center">
          <div class="text-4xl mb-4">⚠️</div>
          <h3 class="text-lg font-semibold mb-2">Weather Data Unavailable</h3>
          <p class="opacity-80">${message}</p>
          <button onclick="window.weatherWidget.refreshWeather()" 
                  class="mt-4 bg-white/20 hover:bg-white/30 text-current px-6 py-2 rounded-lg transition-all duration-200">
            <i class="fas fa-sync-alt mr-2"></i>Try Again
          </button>
        </div>
      `;
      errorElement.classList.remove("hidden");
    }
  }

  hideError() {
    const errorElement = document.getElementById("weather-error");
    if (errorElement) {
      errorElement.classList.add("hidden");
    }
  }

  async loadWeatherByCoordinates(lat, lon) {
    this.currentLocation = { latitude: lat, longitude: lon };
    await this.loadWeather();
  }

  async loadHourlyForecast(hours = 24) {
    try {
      this.currentHours = hours;

      let url = "/api/weather/hourly";
      if (this.currentLocation) {
        url += `?lat=${this.currentLocation.latitude}&lon=${this.currentLocation.longitude}&hours=${hours}`;
      } else {
        url += `?hours=${hours}`;
      }

      console.log("Fetching hourly forecast from:", url);
      const response = await fetch(url);
      const result = await response.json();

      console.log("Hourly forecast API response:", result);

      if (result.success && result.data.hourly) {
        this.displayHourlyForecast(result.data.hourly);
        console.log("Hourly forecast updated successfully");
      } else {
        console.error("Hourly forecast API error:", result.message);
      }
    } catch (error) {
      console.error("Error loading hourly forecast:", error);
    }
  }

  displayHourlyForecast(hourly) {
    if (!hourly || hourly.length === 0) {
      console.log("No hourly data to display");
      return;
    }

    const forecastContainer = document.getElementById("weather-forecast");
    if (!forecastContainer) return;

    const getButtonClass = (targetHours) => {
      return this.currentHours === targetHours
        ? "px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
        : "px-4 py-2 bg-white/20 text-white rounded-lg text-sm font-medium hover:bg-white/30 transition-colors";
    };

    const hourlySection = document.createElement("div");
    hourlySection.innerHTML = `
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-lg mb-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-white flex items-center">
            <i class="fas fa-clock mr-3 text-yellow-400"></i>
            ${this.currentHours}-Hour Forecast
          </h3>
          <div class="flex gap-2">
            <button id="hourly-12h" class="${getButtonClass(12)}">12h</button>
            <button id="hourly-24h" class="${getButtonClass(24)}">24h</button>
            <button id="hourly-48h" class="${getButtonClass(48)}">48h</button>
          </div>
        </div>
        
        <div id="hourly-forecast-container" class="overflow-x-auto">
          <div class="flex gap-4 pb-4" style="min-width: max-content;">
            ${hourly
              .map((hour, index) => {
                const date = new Date(hour.datetime * 1000);
                const timeStr = date.toLocaleTimeString("en-US", {
                  hour: "2-digit",
                  minute: "2-digit",
                  hour12: false,
                });
                const dayStr = date.toLocaleDateString("en-US", {
                  weekday: "short",
                });
                const isToday = date.getDate() === new Date().getDate();

                const theme = this.getWeatherTheme(
                  hour.weather.description,
                  hour.temperature
                );

                return `
                <div class="hourly-item flex-shrink-0 bg-white/10 backdrop-blur-sm rounded-xl p-4 w-24 text-center hover:bg-white/20 transition-colors duration-300">
                  <div class="text-sm text-white/80 mb-2 font-medium">
                    ${isToday && index < 12 ? timeStr : dayStr}
                  </div>
                  <div class="mb-3 relative">
                    <img src="${hour.weather.icon_url}" 
                         alt="${hour.weather.description}" 
                         class="w-10 h-10 mx-auto drop-shadow-md">
                  </div>
                  <div class="text-lg font-bold text-white mb-2">
                    ${hour.temperature}°
                  </div>
                  <div class="text-xs text-white/70 mb-2">
                    ${hour.feels_like}°
                  </div>
                  ${
                    hour.pop > 0
                      ? `
                    <div class="flex items-center justify-center text-xs text-blue-300">
                      <i class="fas fa-tint mr-1"></i>
                      <span>${Math.round(hour.pop * 100)}%</span>
                    </div>
                  `
                      : ""
                  }
                </div>
              `;
              })
              .join("")}
          </div>
        </div>
      </div>
    `;

    const existingHourly = forecastContainer.querySelector(
      ".hourly-forecast-section"
    );
    if (existingHourly) {
      existingHourly.remove();
    }

    hourlySection.className = "hourly-forecast-section mb-8";
    forecastContainer.insertBefore(hourlySection, forecastContainer.firstChild);

    this.bindHourlyEvents();
  }

  bindHourlyEvents() {
    const btn12h = document.getElementById("hourly-12h");
    const btn24h = document.getElementById("hourly-24h");
    const btn48h = document.getElementById("hourly-48h");

    if (btn12h) {
      btn12h.addEventListener("click", () => {
        this.loadHourlyForecast(12);
      });
    }

    if (btn24h) {
      btn24h.addEventListener("click", () => {
        this.loadHourlyForecast(24);
      });
    }

    if (btn48h) {
      btn48h.addEventListener("click", () => {
        this.loadHourlyForecast(48);
      });
    }
  }
}

// Initialize the weather widget
document.addEventListener("DOMContentLoaded", function () {
  window.weatherWidget = new WeatherWidget();
});

// Make loadWeatherByCoordinates globally available
window.loadWeatherByCoordinates = function (lat, lon) {
  if (window.weatherWidget) {
    window.weatherWidget.loadWeatherByCoordinates(lat, lon);
  }
};
