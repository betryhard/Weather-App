document.addEventListener("DOMContentLoaded", function () {
  initializeDropdowns();

  initializeModals();

  initializeFormValidation();

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });

  document.querySelectorAll('button[type="submit"]').forEach((button) => {
    button.addEventListener("click", function () {
      this.style.transform = "scale(0.95)";
      setTimeout(() => {
        this.style.transform = "scale(1)";
      }, 150);
    });
  });

  setTimeout(() => {
    const alerts = document.querySelectorAll('[class*="alert-"]');
    alerts.forEach((alert) => {
      alert.style.transition = "opacity 0.5s ease-out";
      alert.style.opacity = "0";
      setTimeout(() => {
        if (alert.parentNode) {
          alert.parentNode.removeChild(alert);
        }
      }, 500);
    });
  }, 5000);
});

function initializeDropdowns() {
  const dropdowns = document.querySelectorAll(".group");

  dropdowns.forEach((dropdown) => {
    const button = dropdown.querySelector("button");
    const menu = dropdown.querySelector('div[class*="absolute"]');

    if (button && menu) {
      button.addEventListener("click", function (e) {
        e.stopPropagation();

        dropdowns.forEach((otherDropdown) => {
          if (otherDropdown !== dropdown) {
            const otherMenu = otherDropdown.querySelector(
              'div[class*="absolute"]'
            );
            if (otherMenu) {
              otherMenu.classList.add("opacity-0", "invisible");
              otherMenu.classList.remove("opacity-100", "visible");
            }
          }
        });

        menu.classList.toggle("opacity-0");
        menu.classList.toggle("invisible");
        menu.classList.toggle("opacity-100");
        menu.classList.toggle("visible");
      });
    }
  });

  document.addEventListener("click", function (e) {
    dropdowns.forEach((dropdown) => {
      const menu = dropdown.querySelector('div[class*="absolute"]');
      if (menu && !dropdown.contains(e.target)) {
        menu.classList.add("opacity-0", "invisible");
        menu.classList.remove("opacity-100", "visible");
      }
    });
  });
}

function initializeModals() {
  const modalTriggers = document.querySelectorAll("[data-modal-target]");
  const modalCloses = document.querySelectorAll("[data-modal-close]");

  modalTriggers.forEach((trigger) => {
    trigger.addEventListener("click", function () {
      const modalId = this.getAttribute("data-modal-target");
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
      }
    });
  });

  modalCloses.forEach((closeBtn) => {
    closeBtn.addEventListener("click", function () {
      const modal = this.closest(".modal");
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      }
    });
  });

  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("modal")) {
      e.target.classList.add("hidden");
      e.target.classList.remove("flex");
    }
  });
}

function initializeFormValidation() {
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      const requiredFields = form.querySelectorAll("[required]");
      let isValid = true;

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          isValid = false;
          field.classList.add("border-red-500");
          field.classList.remove("border-gray-300");
        } else {
          field.classList.remove("border-red-500");
          field.classList.add("border-gray-300");
        }
      });

      const password = form.querySelector('input[name="password"]');
      const confirmPassword = form.querySelector(
        'input[name="confirm_password"]'
      );

      if (
        password &&
        confirmPassword &&
        password.value !== confirmPassword.value
      ) {
        isValid = false;
        confirmPassword.classList.add("border-red-500");
        confirmPassword.classList.remove("border-gray-300");

        showFormError(confirmPassword, "Passwords do not match");
      }

      if (!isValid) {
        e.preventDefault();
      }
    });
  });
}

function showFormError(field, message) {
  const existingError = field.parentNode.querySelector(".error-message");
  if (existingError) {
    existingError.remove();
  }

  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message text-red-500 text-sm mt-1";
  errorDiv.textContent = message;

  field.parentNode.appendChild(errorDiv);

  field.addEventListener("input", function () {
    if (errorDiv.parentNode) {
      errorDiv.remove();
    }
    field.classList.remove("border-red-500");
    field.classList.add("border-gray-300");
  });
}

function fetchUsers() {
  return fetch("/admin/api/users")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Users data:", data);
      return data;
    })
    .catch((error) => {
      console.error("Error fetching users:", error);
      showNotification("Error fetching users", "error");
    });
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;

  switch (type) {
    case "success":
      notification.classList.add(
        "bg-green-100",
        "border",
        "border-green-400",
        "text-green-700"
      );
      break;
    case "error":
      notification.classList.add(
        "bg-red-100",
        "border",
        "border-red-400",
        "text-red-700"
      );
      break;
    case "warning":
      notification.classList.add(
        "bg-yellow-100",
        "border",
        "border-yellow-400",
        "text-yellow-700"
      );
      break;
    default:
      notification.classList.add(
        "bg-blue-100",
        "border",
        "border-blue-400",
        "text-blue-700"
      );
  }

  notification.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-gray-500 hover:text-gray-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.classList.remove("translate-x-full");
  }, 100);

  setTimeout(() => {
    notification.classList.add("translate-x-full");
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

window.fetchUsers = fetchUsers;
window.showNotification = showNotification;
