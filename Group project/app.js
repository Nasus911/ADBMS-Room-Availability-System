const users = [
  { name: "System Admin", username: "admin", password: "admin123", role: "Admin", status: "Active", lastLogin: "Mar 14" },
  { name: "Prof. Santos", username: "psantos", password: "prof123", role: "Professor", status: "Active", lastLogin: "Mar 14" },
  { name: "Juan Dela Cruz", username: "jdc", password: "student123", role: "Student", status: "Active", lastLogin: "Mar 13" },
];

const rooms = [
  { room: 401, occupiedBy: null },
  { room: 402, occupiedBy: null },
  { room: 407, occupiedBy: "psantos" },
  { room: 408, occupiedBy: null },
];

let currentUser = null;

const loginScreen = document.getElementById("loginScreen");
const adminDashboard = document.getElementById("adminDashboard");
const professorDashboard = document.getElementById("professorDashboard");
const studentDashboard = document.getElementById("studentDashboard");

const loginForm = document.getElementById("loginForm");
const loginUsername = document.getElementById("loginUsername");
const loginPassword = document.getElementById("loginPassword");
const loginError = document.getElementById("loginError");

const adminWelcome = document.getElementById("adminWelcome");
const professorWelcome = document.getElementById("professorWelcome");
const studentInfoEl = document.getElementById("studentInfo");

const adminRoomBody = document.getElementById("adminRoomBody");
const usersBody = document.getElementById("usersBody");
const profRoomBody = document.getElementById("profRoomBody");
const studentRoomBody = document.getElementById("studentRoomBody");
const studentNote = document.getElementById("studentNote");

const navItems = document.querySelectorAll("[data-admin-view]");
const adminViews = {
  dashboard: document.getElementById("adminViewDashboard"),
  manage: document.getElementById("adminViewManage"),
  reports: document.getElementById("adminViewReports"),
  settings: document.getElementById("adminViewSettings"),
};

const addUserModal = document.getElementById("addUserModal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const cancelModalBtn = document.getElementById("cancelModalBtn");
const userForm = document.getElementById("userForm");
const userFormError = document.getElementById("userFormError");
const passwordToggles = document.querySelectorAll("[data-toggle-password]");

const adminLogoutBtn = document.getElementById("adminLogoutBtn");
const profLogoutBtn = document.getElementById("profLogoutBtn");
const studentLogoutBtn = document.getElementById("studentLogoutBtn");

function getUserByUsername(username) {
  return users.find((user) => user.username.toLowerCase() === username.toLowerCase());
}

function formatToday() {
  return new Date().toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function hideAllDashboards() {
  adminDashboard.classList.add("hidden");
  professorDashboard.classList.add("hidden");
  studentDashboard.classList.add("hidden");
}

function showLogin() {
  currentUser = null;
  hideAllDashboards();
  loginScreen.classList.remove("hidden");
  loginForm.reset();
  loginError.classList.add("hidden");
  closeUserModal();
}

function showDashboardForUser(user) {
  hideAllDashboards();
  loginScreen.classList.add("hidden");

  if (user.role === "Admin") {
    adminWelcome.textContent = `Welcome, ${user.name}!`;
    adminDashboard.classList.remove("hidden");
    switchAdminView("dashboard");
    renderAdminRooms();
    renderUsersTable();
    return;
  }

  if (user.role === "Professor") {
    professorWelcome.textContent = `Welcome, ${user.name}!`;
    professorDashboard.classList.remove("hidden");
    renderProfessorRooms();
    return;
  }

  studentDashboard.classList.remove("hidden");
  // populate student header info
  try {
    if (studentInfoEl) {
      var program = user.program || user.degree || 'N/A';
      var block = user.block || user.section || 'N/A';
      studentInfoEl.querySelector('.student-name')?.textContent = user.name || 'Student';
      studentInfoEl.querySelector('.student-meta')?.textContent = block + ' • ' + program;
    }
  } catch (e) {}

  renderStudentRooms();
}

function switchAdminView(view) {
  Object.entries(adminViews).forEach(([key, element]) => {
    element.classList.toggle("hidden", key !== view);
  });

  navItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.adminView === view);
  });
}

function getProfessorOptions() {
  return users.filter((user) => user.role === "Professor" && user.status === "Active");
}

function getRoomStatus(room) {
  return room.occupiedBy ? "Occupied" : "Available";
}

function getOccupantName(username) {
  if (!username) {
    return "";
  }
  const user = getUserByUsername(username);
  return user ? user.name : "Unknown";
}

function renderUsersTable() {
  usersBody.innerHTML = users
    .map(
      (user) => `
      <tr class="${user.status === "Inactive" ? "inactive-user-row" : ""}">
        <td>${user.name}</td>
        <td>${user.username}</td>
        <td>${user.role}</td>
        <td>
          <span class="status-pill ${user.status === "Active" ? "status-active" : "status-inactive"}">
            ${user.status}
          </span>
        </td>
        <td>${user.lastLogin || "-"}</td>
        <td>
          ${
            user.username === "admin"
              ? '<span class="action-note">Primary admin</span>'
              : user.status === "Active"
                ? `<button class="danger-btn user-toggle-btn" data-user-action="deactivate" data-username="${user.username}">Deactivate</button>`
                : `<button class="action-btn user-toggle-btn" data-user-action="reactivate" data-username="${user.username}">Reactivate</button>`
          }
        </td>
      </tr>`
    )
    .join("");
}

function releaseRoomsForUser(username) {
  rooms.forEach((room) => {
    if (room.occupiedBy === username) {
      room.occupiedBy = null;
    }
  });
}

function syncAllDashboards() {
  renderAdminRooms();
  renderUsersTable();

  if (!professorDashboard.classList.contains("hidden") && currentUser?.role === "Professor") {
    renderProfessorRooms();
  }

  if (!studentDashboard.classList.contains("hidden")) {
    renderStudentRooms();
  }
}

function renderAdminRooms() {
  adminRoomBody.innerHTML = rooms
    .map((room) => {
      const isOccupied = Boolean(room.occupiedBy);
      return `
      <tr data-room="${room.room}" class="${isOccupied ? "occupied-row" : ""}">
        <td>${room.room}</td>
        <td class="${isOccupied ? "occupied" : "available"}">${getRoomStatus(room)}</td>
        <td>${getOccupantName(room.occupiedBy)}</td>
        <td>
          ${
            isOccupied
              ? `<button class="danger-btn" data-admin-action="release" data-room="${room.room}">Force Release</button>`
              : `<button class="action-btn" data-admin-action="checkin" data-room="${room.room}">Check In</button>`
          }
        </td>
      </tr>`;
    })
    .join("");
}

function renderProfessorRooms() {
  profRoomBody.innerHTML = rooms
    .map((room) => {
      const occupiedByCurrentUser = room.occupiedBy === currentUser.username;
      const occupiedByOther = room.occupiedBy && !occupiedByCurrentUser;

      return `
      <tr data-room="${room.room}" class="${occupiedByCurrentUser ? "occupied-row" : ""}">
        <td>
          <strong>Room ${room.room}</strong>
          ${occupiedByCurrentUser ? '<span class="badge">Occupied (You)</span>' : ""}
        </td>
        <td class="${room.occupiedBy ? "occupied" : "available"}">
          ${
            occupiedByCurrentUser
              ? "Occupied (You)"
              : room.occupiedBy
                ? `Occupied (${getOccupantName(room.occupiedBy)})`
                : "Available"
          }
        </td>
        <td>
          ${
            occupiedByCurrentUser
              ? `<button class="action-btn" data-prof-action="checkout" data-room="${room.room}">Checked In</button>`
              : occupiedByOther
                ? ""
                : `<button class="action-btn" data-prof-action="checkin" data-room="${room.room}">Check In</button>`
          }
        </td>
      </tr>`;
    })
    .join("");
}

function renderStudentRooms() {
  studentRoomBody.innerHTML = rooms
    .map(
      (room) => `
      <tr data-room="${room.room}" class="${room.occupiedBy ? "occupied-row" : ""}">
        <td><strong>Room ${room.room}</strong></td>
        <td class="${room.occupiedBy ? "occupied" : "available"}">${getRoomStatus(room)}</td>
      </tr>`
    )
    .join("");

  const occupiedRoom = rooms.find((room) => room.occupiedBy);
  studentNote.textContent = occupiedRoom
    ? `🗓 Room ${occupiedRoom.room} is currently occupied by a professor.`
    : "🗓 All rooms are currently available.";
}

// Flash a table row to call attention to a recent change
function flashRoomRow(roomNumber) {
  try {
    const selectors = [adminRoomBody, profRoomBody, studentRoomBody];
    selectors.forEach((body) => {
      if (!body) return;
      const row = body.querySelector(`tr[data-room="${roomNumber}"]`);
      if (row) {
        row.classList.add("row-flash");
        // remove the class after the animation completes to allow retrigger
        setTimeout(() => row.classList.remove("row-flash"), 1100);
      }
    });
  } catch (e) {
    // silent fail - UI enhancement only
  }
}

// transient on-page note for check-in/check-out actions
function showActionNote(message) {
  try {
    let el = document.getElementById('actionNote');
    if (!el) {
      el = document.createElement('div');
      el.id = 'actionNote';
      el.className = 'action-note-toast';
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.add('visible');
    setTimeout(() => { el.classList.remove('visible'); }, 4500);
  } catch (e) {}
}

function rerenderVisibleDashboard() {
  if (!currentUser) {
    return;
  }

  if (currentUser.role === "Admin") {
    renderAdminRooms();
    renderUsersTable();
  }

  if (currentUser.role === "Professor") {
    renderProfessorRooms();
  }

  if (currentUser.role === "Student") {
    renderStudentRooms();
  }
}

function closeUserModal() {
  addUserModal.classList.add("hidden");
  userFormError.textContent = "";
  userFormError.classList.add("hidden");
}

function openUserModal() {
  addUserModal.classList.remove("hidden");
  userFormError.textContent = "";
  userFormError.classList.add("hidden");
}

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const username = loginUsername.value.trim();
  const password = loginPassword.value;

  const user = users.find(
    (candidate) => candidate.username.toLowerCase() === username.toLowerCase() && candidate.password === password
  );

  if (!user) {
    loginError.textContent = "Invalid username or password.";
    loginError.classList.remove("hidden");
    return;
  }

  if (user.status !== "Active") {
    loginError.textContent = "This account is inactive. Contact the admin.";
    loginError.classList.remove("hidden");
    return;
  }

  loginError.classList.add("hidden");
  loginError.textContent = "Invalid username or password.";
  currentUser = user;
  currentUser.lastLogin = formatToday();
  showDashboardForUser(user);
});

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    switchAdminView(item.dataset.adminView);
  });
});

openModalBtn.addEventListener("click", openUserModal);
closeModalBtn.addEventListener("click", closeUserModal);
cancelModalBtn.addEventListener("click", closeUserModal);

passwordToggles.forEach((toggle) => {
  toggle.addEventListener("click", () => {
    const input = document.getElementById(toggle.dataset.togglePassword);

    if (!input) {
      return;
    }

    const isVisible = input.type === "text";
    input.type = isVisible ? "password" : "text";
    toggle.textContent = isVisible ? "👁" : "🙈";
  });
});

userForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const fullName = document.getElementById("fullName").value.trim();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const role = document.getElementById("roleSelect").value;

  userFormError.textContent = "";
  userFormError.classList.add("hidden");

  if (!fullName || !username || !password || !confirmPassword || !role) {
    return;
  }

  if (password !== confirmPassword) {
    userFormError.textContent = "Passwords do not match.";
    userFormError.classList.remove("hidden");
    return;
  }

  if (getUserByUsername(username)) {
    userFormError.textContent = "Username already exists. Use a different username.";
    userFormError.classList.remove("hidden");
    return;
  }

  users.push({
    name: fullName,
    username,
    password,
    role,
    status: "Active",
    lastLogin: "-",
  });

  userForm.reset();
  passwordToggles.forEach((toggle) => {
    toggle.textContent = "👁";
  });
  closeUserModal();
  rerenderVisibleDashboard();
});

adminRoomBody.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const roomNumber = Number(target.dataset.room);
  const action = target.dataset.adminAction;
  const room = rooms.find((item) => item.room === roomNumber);

  if (!room) {
    return;
  }

  if (action === "release") {
    room.occupiedBy = null;
    showActionNote(`Room ${roomNumber} released (check-out)`);
  }

  if (action === "checkin") {
    const professors = getProfessorOptions();
    if (professors.length === 0) {
      window.alert("No professor account found. Add a professor first.");
      return;
    }
    room.occupiedBy = professors[0].username;
    showActionNote(`Room ${roomNumber} checked in to ${getOccupantName(room.occupiedBy)}`);
  }

  syncAllDashboards();
  flashRoomRow(roomNumber);
});

profRoomBody.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const roomNumber = Number(target.dataset.room);
  const action = target.dataset.profAction;
  const selectedRoom = rooms.find((item) => item.room === roomNumber);

  if (!selectedRoom) {
    return;
  }

  if (action === "checkout" && selectedRoom.occupiedBy === currentUser.username) {
    selectedRoom.occupiedBy = null;
  }

  if (action === "checkin" && !selectedRoom.occupiedBy) {
    rooms.forEach((room) => {
      if (room.occupiedBy === currentUser.username) {
        room.occupiedBy = null;
      }
    });
    selectedRoom.occupiedBy = currentUser.username;
  }

  renderProfessorRooms();
  if (!adminDashboard.classList.contains("hidden")) {
    renderAdminRooms();
  }
  if (!studentDashboard.classList.contains("hidden")) {
    renderStudentRooms();
  }
  flashRoomRow(roomNumber);
});

usersBody.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const username = target.dataset.username;
  const action = target.dataset.userAction;
  const user = getUserByUsername(username);

  if (!user || user.username === "admin") {
    return;
  }

  if (action === "deactivate") {
    user.status = "Inactive";
    releaseRoomsForUser(user.username);
  }

  if (action === "reactivate") {
    user.status = "Active";
  }

  syncAllDashboards();
});

adminLogoutBtn.addEventListener("click", showLogin);
adminLogoutBtn.addEventListener("click", function(){ if (confirm('Confirm log out?')) showLogin(); });
profLogoutBtn.addEventListener("click", function(){ if (confirm('Confirm log out?')) showLogin(); });
studentLogoutBtn.addEventListener("click", function(){ if (confirm('Confirm log out?')) showLogin(); });

showLogin();
