class FavoritesManager {
  constructor() {
    this.currentUser = null;
    this.currentWeatherLocation = null;
    this.selectedLocationInfo = null; // Store location info from search results
    this.init();
  }

  init() {
    this.checkUserAuth();
    this.bindEvents();
    this.loadUserFavorites();
  }

  checkUserAuth() {
    // Check if user is logged in by looking for user data in page
    const userElement = document.querySelector("[data-user-id]");
    if (userElement) {
      this.currentUser = {
        id: userElement.getAttribute("data-user-id"),
        isAuthenticated: true,
      };
    } else {
      this.currentUser = { isAuthenticated: false };
    }
  }

  bindEvents() {
    // Listen for weather data updates to show/hide favorite button
    document.addEventListener("weatherUpdated", (event) => {
      this.currentWeatherLocation = event.detail;
      this.updateFavoriteButton();
    });

    // Bind favorite button click
    document.addEventListener("click", (event) => {
      if (event.target.closest("#favorite-btn")) {
        event.preventDefault();
        this.toggleFavorite();
      }
    });

    // Bind favorites modal button
    document.addEventListener("click", (event) => {
      if (event.target.closest("#favorites-modal-btn")) {
        this.showFavoritesModal();
      }
    });

    // Bind modal close buttons
    document.addEventListener("click", (event) => {
      if (
        event.target.closest("#close-favorites-modal") ||
        event.target.closest("#close-favorites-modal-btn")
      ) {
        this.hideFavoritesModal();
      }
    });

    // Close modal when clicking outside
    document.addEventListener("click", (event) => {
      const modal = document.getElementById("favorites-modal");
      if (event.target === modal) {
        this.hideFavoritesModal();
      }
    });

    // Close modal with ESC key
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        this.hideFavoritesModal();
      }
    });

    // Bind favorites list item clicks
    document.addEventListener("click", (event) => {
      const favoriteItem = event.target.closest(".favorite-item");
      if (favoriteItem) {
        const lat = parseFloat(favoriteItem.dataset.lat);
        const lon = parseFloat(favoriteItem.dataset.lon);
        const locationName = favoriteItem.dataset.locationName;
        const country = favoriteItem.dataset.country || "";
        this.loadWeatherFromFavorite(lat, lon, locationName, country);

        // Close modal if this was clicked in modal
        if (favoriteItem.closest("#favorites-modal")) {
          this.hideFavoritesModal();
        }
      }
    });

    // Bind remove favorite buttons
    document.addEventListener("click", (event) => {
      if (event.target.closest(".remove-favorite-btn")) {
        event.preventDefault();
        event.stopPropagation();
        const favoriteItem = event.target.closest(".favorite-item");
        const lat = parseFloat(favoriteItem.dataset.lat);
        const lon = parseFloat(favoriteItem.dataset.lon);
        this.removeFavorite(lat, lon);
      }
    });
  }

  async loadUserFavorites() {
    if (!this.currentUser.isAuthenticated) {
      this.hideFavoritesList();
      return;
    }

    try {
      const response = await fetch("/api/favorites");
      const result = await response.json();

      if (result.success) {
        this.displayFavoritesList(result.data);
      } else {
        console.error("Error loading favorites:", result.message);
      }
    } catch (error) {
      console.error("Error loading favorites:", error);
    }
  }

  displayFavoritesList(favorites) {
    if (!favorites || favorites.length === 0) {
      this.showEmptyFavorites();
      return;
    }

    const favoritesContainer = this.getFavoritesContainer();
    if (!favoritesContainer) return;

    const favoritesList = favorites
      .map((fav, index) => {
        // Create a gradient for each item
        const gradients = [
          "from-blue-500/20 to-purple-500/20",
          "from-green-500/20 to-teal-500/20",
          "from-orange-500/20 to-red-500/20",
          "from-purple-500/20 to-pink-500/20",
          "from-indigo-500/20 to-blue-500/20",
        ];
        const gradient = gradients[index % gradients.length];

        return `
                      <div class="favorite-item group bg-gradient-to-r ${gradient} backdrop-blur-md rounded-xl p-5 cursor-pointer hover:scale-[1.02] transition-all duration-300 border border-white/30 hover:border-white/50 shadow-lg hover:shadow-xl" 
                data-lat="${fav.latitude}" data-lon="${
          fav.longitude
        }" data-location-name="${fav.location_name}" data-country="${
          fav.country || ""
        }">
              <div class="flex items-center justify-between">
              <div class="flex items-center flex-1">
                <div class="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mr-4 shadow-md">
                  <i class="fas fa-map-marker-alt text-white text-lg"></i>
                </div>
                <div class="flex-1">
                  <div class="flex items-center mb-1">
                    <h5 class="text-white font-bold text-lg group-hover:text-yellow-200 transition-colors">
                      ${fav.location_name}
                    </h5>
                    <i class="fas fa-star text-yellow-400 ml-2 text-sm"></i>
                  </div>
                  ${
                    fav.country
                      ? `
                    <p class="text-white/80 text-sm font-medium flex items-center">
                      <i class="fas fa-globe-asia mr-1 text-white/60"></i>
                      ${fav.country}
                    </p>
                  `
                      : ""
                  }
                  <p class="text-white/60 text-xs mt-1 flex items-center">
                    <i class="fas fa-crosshairs mr-1"></i>
                    ${fav.latitude.toFixed(4)}, ${fav.longitude.toFixed(4)}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <button class="remove-favorite-btn text-red-400 hover:text-red-300 p-3 rounded-xl hover:bg-red-500/20 transition-all duration-200 opacity-0 group-hover:opacity-100" 
                        title="Remove from favorites">
                  <i class="fas fa-trash text-sm"></i>
                </button>
                <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center group-hover:bg-white/30 transition-colors">
                  <i class="fas fa-chevron-right text-white/70 text-sm"></i>
                </div>
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    favoritesContainer.innerHTML = `
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-white flex items-center">
            <div class="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center mr-3 shadow-lg">
              <i class="fas fa-heart text-white"></i>
            </div>
            Favorite Locations
          </h3>
          <div class="bg-white/20 px-4 py-2 rounded-full">
            <span class="text-white font-bold text-sm">${favorites.length} locations</span>
          </div>
        </div>
        <div class="space-y-4">
          ${favoritesList}
        </div>
        <div class="mt-6 p-4 bg-white/10 rounded-xl border border-white/20">
          <p class="text-white/70 text-sm flex items-center">
            <i class="fas fa-info-circle mr-2 text-blue-300"></i>
            Click on a location to view detailed weather information
          </p>
        </div>
      </div>
    `;
  }

  showEmptyFavorites() {
    const favoritesContainer = this.getFavoritesContainer();
    if (!favoritesContainer) return;

    favoritesContainer.innerHTML = `
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-12 border border-white/20 text-center shadow-2xl">
        <div class="w-20 h-20 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
          <i class="fas fa-heart text-white text-2xl"></i>
        </div>
        <h3 class="text-2xl font-bold text-white mb-3">No Favorite Locations</h3>
        <p class="text-white/70 text-lg mb-6 max-w-md mx-auto">Add favorite locations for quick access to weather information</p>
        <div class="bg-white/10 rounded-xl p-6 border border-white/20">
          <div class="flex items-center justify-center mb-4">
            <div class="flex items-center gap-4">
              <div class="flex items-center">
                <div class="w-8 h-8 bg-blue-500/30 rounded-full flex items-center justify-center mr-2">
                  <span class="text-white font-bold text-sm">1</span>
                </div>
                <span class="text-white/80 text-sm">Search location</span>
              </div>
              <i class="fas fa-arrow-right text-white/60"></i>
              <div class="flex items-center">
                <div class="w-8 h-8 bg-green-500/30 rounded-full flex items-center justify-center mr-2">
                  <span class="text-white font-bold text-sm">2</span>
                </div>
                <span class="text-white/80 text-sm">Click star ⭐</span>
              </div>
            </div>
          </div>
          <p class="text-white/60 text-sm">
            Guide: Search for any location, then click the star icon on the weather card to add to favorites
          </p>
        </div>
      </div>
    `;
  }

  hideFavoritesList() {
    const favoritesContainer = this.getFavoritesContainer();
    if (favoritesContainer) {
      favoritesContainer.style.display = "none";
    }
  }

  getFavoritesContainer() {
    // Return null to disable page favorites list (only use modal)
    return null;
  }

  updateFavoriteButton() {
    if (!this.currentUser.isAuthenticated || !this.currentWeatherLocation) {
      this.hideFavoriteButton();
      return;
    }

    this.checkCurrentLocationFavoriteStatus();
  }

  async checkCurrentLocationFavoriteStatus() {
    if (!this.currentWeatherLocation) return;

    try {
      const { latitude, longitude } = this.currentWeatherLocation;
      const response = await fetch(
        `/api/favorites/check?lat=${latitude}&lon=${longitude}`
      );
      const result = await response.json();

      if (result.success) {
        this.showFavoriteButton(result.is_favorite);
      }
    } catch (error) {
      console.error("Error checking favorite status:", error);
    }
  }

  showFavoriteButton(isFavorite = false) {
    const currentWeatherContainer = document.getElementById("current-weather");
    if (!currentWeatherContainer) return;

    // Remove existing favorite button
    const existingBtn = currentWeatherContainer.querySelector("#favorite-btn");
    if (existingBtn) {
      existingBtn.remove();
    }

    // Find the weather card title area to insert the button
    const weatherCard =
      currentWeatherContainer.querySelector(".weather-card-main");
    if (!weatherCard) return;

    const titleArea = weatherCard.querySelector("h3");
    if (!titleArea) return;

    const favoriteBtn = document.createElement("button");
    favoriteBtn.id = "favorite-btn";
    favoriteBtn.className = `ml-4 p-2 rounded-lg transition-all duration-200 ${
      isFavorite
        ? "bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30"
        : "bg-white/10 text-white/70 hover:bg-white/20 hover:text-white"
    }`;
    favoriteBtn.innerHTML = `<i class="fas fa-star"></i>`;
    favoriteBtn.title = isFavorite
      ? "Xóa khỏi yêu thích"
      : "Thêm vào yêu thích";

    titleArea.appendChild(favoriteBtn);
  }

  hideFavoriteButton() {
    const favoriteBtn = document.getElementById("favorite-btn");
    if (favoriteBtn) {
      favoriteBtn.remove();
    }
  }

  async toggleFavorite() {
    if (!this.currentUser.isAuthenticated || !this.currentWeatherLocation) {
      this.showNotification(
        "Vui lòng đăng nhập để sử dụng tính năng này",
        "warning"
      );
      return;
    }

    const { latitude, longitude } = this.currentWeatherLocation;

    // Use location info from search results if available, otherwise fallback to reverse geocoding
    let locationName = "Unknown Location";
    let country = "";
    let state = "";

    if (this.selectedLocationInfo) {
      locationName = this.selectedLocationInfo.location_name;
      country = this.selectedLocationInfo.country;
      state = this.selectedLocationInfo.state;
    } else {
      // Fallback to current weather location info
      locationName =
        this.currentWeatherLocation.location_name || "Current Location";
      country = this.currentWeatherLocation.country || "";
      state = this.currentWeatherLocation.state || "";
    }

    try {
      // Check current status first
      const checkResponse = await fetch(
        `/api/favorites/check?lat=${latitude}&lon=${longitude}`
      );
      const checkResult = await checkResponse.json();

      let response, result;

      if (checkResult.success && checkResult.is_favorite) {
        // Remove from favorites
        response = await fetch("/api/favorites", {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
          }),
        });
        result = await response.json();

        if (result.success) {
          this.showNotification("Removed from favorites", "success");
          this.showFavoriteButton(false);
        }
      } else {
        // Add to favorites
        response = await fetch("/api/favorites", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            location_name: locationName,
            latitude: latitude,
            longitude: longitude,
            country: country,
            state: state,
          }),
        });
        result = await response.json();

        if (result.success) {
          this.showNotification("Added to favorites", "success");
          this.showFavoriteButton(true);
        }
      }

      if (!result.success) {
        this.showNotification(result.message || "An error occurred", "error");
      }

      // Reload favorites list
      this.loadUserFavorites();

      // Update modal if it's open
      const modal = document.getElementById("favorites-modal");
      if (modal && !modal.classList.contains("hidden")) {
        this.loadFavoritesForModal();
      }

      // Clear selected location info after use
      this.selectedLocationInfo = null;
    } catch (error) {
      console.error("Error toggling favorite:", error);
      this.showNotification("Error processing request", "error");
    }
  }

  async removeFavorite(latitude, longitude) {
    if (!this.currentUser.isAuthenticated) return;

    try {
      const response = await fetch("/api/favorites", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude: latitude,
          longitude: longitude,
        }),
      });

      const result = await response.json();

      if (result.success) {
        this.showNotification("Removed from favorites", "success");
        this.loadUserFavorites();

        // Update modal if it's open
        const modal = document.getElementById("favorites-modal");
        if (modal && !modal.classList.contains("hidden")) {
          this.loadFavoritesForModal();
        }

        // Update favorite button if this location is currently displayed
        if (
          this.currentWeatherLocation &&
          Math.abs(this.currentWeatherLocation.latitude - latitude) < 0.0001 &&
          Math.abs(this.currentWeatherLocation.longitude - longitude) < 0.0001
        ) {
          this.showFavoriteButton(false);
        }
      } else {
        this.showNotification(result.message || "An error occurred", "error");
      }
    } catch (error) {
      console.error("Error removing favorite:", error);
      this.showNotification("Error removing location", "error");
    }
  }

  async loadWeatherFromFavorite(latitude, longitude, locationName, country) {
    // Store the selected location info for favorites
    this.selectedLocationInfo = {
      location_name: locationName || "Unknown Location",
      country: country || "",
      state: "",
    };

    // Use the weather widget's loadWeatherByCoordinates method
    if (
      window.weatherWidget &&
      typeof window.weatherWidget.loadWeatherByCoordinates === "function"
    ) {
      window.weatherWidget.loadWeatherByCoordinates(latitude, longitude);
    }

    // Update current location display immediately with the correct name
    if (window.locationSearchManager) {
      const locationData = {
        lat: latitude,
        lon: longitude,
        address: {
          city: locationName || "Unknown Location",
          country: country || "",
        },
      };
      window.locationSearchManager.updateCurrentLocationDisplay(locationData);
    }
  }

  showNotification(message, type = "info") {
    const iconMap = {
      info: "info-circle text-blue-500",
      warning: "exclamation-triangle text-yellow-500",
      error: "exclamation-circle text-red-500",
      success: "check-circle text-green-500",
    };

    const notification = document.createElement("div");
    notification.className = `fixed top-24 right-4 z-50 bg-white/90 backdrop-blur-md rounded-lg shadow-xl p-4 border border-white/20 transform translate-x-full transition-transform duration-300`;
    notification.innerHTML = `
      <div class="flex items-center">
        <i class="fas fa-${iconMap[type] || iconMap.info} mr-2"></i>
        <span class="text-gray-800">${message}</span>
      </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.remove("translate-x-full");
    }, 100);

    // Remove after 3 seconds
    setTimeout(() => {
      notification.classList.add("translate-x-full");
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }

  async showFavoritesModal() {
    const modal = document.getElementById("favorites-modal");
    if (!modal) return;

    // Show modal
    modal.classList.remove("hidden");
    setTimeout(() => {
      modal.classList.remove("opacity-0");
    }, 10);

    // Load favorites for modal
    await this.loadFavoritesForModal();
  }

  hideFavoritesModal() {
    const modal = document.getElementById("favorites-modal");
    if (!modal) return;

    modal.classList.add("opacity-0");
    setTimeout(() => {
      modal.classList.add("hidden");
    }, 300);
  }

  async loadFavoritesForModal() {
    const contentEl = document.getElementById("modal-favorites-content");
    if (!contentEl) return;

    try {
      const response = await fetch("/api/favorites");
      const result = await response.json();

      if (result.success) {
        this.displayFavoritesInModal(result.data);
      } else {
        contentEl.innerHTML = `
          <div class="text-center py-8">
            <i class="fas fa-exclamation-triangle text-red-400 text-3xl mb-4"></i>
            <p class="text-white">Error loading favorites</p>
            <p class="text-white/60 text-sm mt-2">${result.message}</p>
          </div>
        `;
      }
    } catch (error) {
      console.error("Error loading favorites for modal:", error);
      contentEl.innerHTML = `
        <div class="text-center py-8">
          <i class="fas fa-exclamation-triangle text-red-400 text-3xl mb-4"></i>
          <p class="text-white">Error connecting to server</p>
          <p class="text-white/60 text-sm mt-2">Please try again later</p>
        </div>
      `;
    }
  }

  displayFavoritesInModal(favorites) {
    const contentEl = document.getElementById("modal-favorites-content");
    if (!contentEl) return;

    if (!favorites || favorites.length === 0) {
      contentEl.innerHTML = `
        <div class="text-center py-12">
          <div class="w-20 h-20 bg-gradient-to-br from-gray-400/20 to-gray-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-heart text-white/40 text-2xl"></i>
          </div>
          <h3 class="text-xl font-bold text-white mb-3">No Favorite Locations</h3>
          <p class="text-white/70 mb-6 max-w-md mx-auto">Add favorite locations for quick access to weather information</p>
          <div class="bg-white/10 rounded-xl p-6 border border-white/20 max-w-md mx-auto">
                          <p class="text-white/60 text-sm">
                Guide: Search for any location, then click the star icon on the weather card to add to favorites
              </p>
          </div>
        </div>
      `;
      return;
    }

    const favoritesList = favorites
      .map((fav, index) => {
        const gradients = [
          "from-blue-500/20 to-purple-500/20",
          "from-green-500/20 to-teal-500/20",
          "from-orange-500/20 to-red-500/20",
          "from-purple-500/20 to-pink-500/20",
          "from-indigo-500/20 to-blue-500/20",
        ];
        const gradient = gradients[index % gradients.length];

        return `
          <div class="favorite-item group bg-gradient-to-r ${gradient} backdrop-blur-md rounded-xl p-4 cursor-pointer hover:scale-[1.02] transition-all duration-300 border border-white/30 hover:border-white/50 shadow-lg hover:shadow-xl" 
               data-lat="${fav.latitude}" data-lon="${
          fav.longitude
        }" data-location-name="${fav.location_name}" data-country="${
          fav.country || ""
        }">
            <div class="flex items-center justify-between">
              <div class="flex items-center flex-1">
                <div class="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mr-3 shadow-md">
                  <i class="fas fa-map-marker-alt text-white"></i>
                </div>
                <div class="flex-1">
                  <div class="flex items-center mb-1">
                    <h5 class="text-white font-bold group-hover:text-yellow-200 transition-colors">
                      ${fav.location_name}
                    </h5>
                    <i class="fas fa-star text-yellow-400 ml-2 text-xs"></i>
                  </div>
                  ${
                    fav.country
                      ? `
                    <p class="text-white/80 text-sm flex items-center">
                      <i class="fas fa-globe-asia mr-1 text-white/60"></i>
                      ${fav.country}
                    </p>
                  `
                      : ""
                  }
                  <p class="text-white/60 text-xs mt-1 flex items-center">
                    <i class="fas fa-crosshairs mr-1"></i>
                    ${fav.latitude.toFixed(4)}, ${fav.longitude.toFixed(4)}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button class="remove-favorite-btn text-red-400 hover:text-red-300 p-2 rounded-lg hover:bg-red-500/20 transition-all duration-200 opacity-0 group-hover:opacity-100" 
                        title="Remove from favorites">
                  <i class="fas fa-trash text-xs"></i>
                </button>
                <div class="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center group-hover:bg-white/30 transition-colors">
                  <i class="fas fa-chevron-right text-white/70 text-xs"></i>
                </div>
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    contentEl.innerHTML = `
      <div class="space-y-3">
        ${favoritesList}
      </div>
    `;
  }
}

// Initialize favorites manager when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.favoritesManager = new FavoritesManager();
});

// Add method to update weather location data
window.updateWeatherLocationForFavorites = (locationData) => {
  if (window.favoritesManager) {
    window.favoritesManager.currentWeatherLocation = locationData;
    window.favoritesManager.updateFavoriteButton();
  }
};
