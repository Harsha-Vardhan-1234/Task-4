const API_BASE = "http://127.0.0.1:5000";

// ------------------ LOAD DOCTORS ------------------
async function loadDoctors() {
  const res = await fetch(`${API_BASE}/api/doctors`);
  const doctors = await res.json();
  const table = document.getElementById("doctorTable");
  table.innerHTML = "";

  doctors.forEach(d => {
    table.innerHTML += `
      <tr>
        <td>${d.id}</td>
        <td>${d.name}</td>
        <td>${d.specialization}</td>
        <td>${d.hospital_name || "N/A"}</td>
        <td>${d.contact || "-"}</td>
        <td><button class="btn btn-danger btn-sm" onclick="deleteDoctor(${d.id})">Delete</button></td>
      </tr>
    `;
  });
}

document.getElementById("addDoctorForm")?.addEventListener("submit", async e => {
  e.preventDefault();
  const payload = {
    name: name.value,
    specialization: specialization.value,
    experience: experience.value,
    hospital_id: hospital_id.value,
    contact: contact.value,
    email: email.value
  };
  await fetch(`${API_BASE}/api/doctors`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  alert("Doctor added!");
  e.target.reset();
  loadDoctors();
});

async function deleteDoctor(id) {
  if (!confirm("Delete this doctor?")) return;
  await fetch(`${API_BASE}/api/doctors/${id}`, {method: "DELETE"});
  loadDoctors();
}

// ------------------ LOAD HOSPITALS ------------------
async function loadHospitals() {
  const res = await fetch(`${API_BASE}/api/hospitals`);
  const hospitals = await res.json();
  const table = document.getElementById("hospitalTable");
  table.innerHTML = "";

  hospitals.forEach(h => {
    table.innerHTML += `
      <tr>
        <td>${h.id}</td>
        <td>${h.name}</td>
        <td>${h.address}</td>
        <td><button class="btn btn-danger btn-sm" onclick="deleteHospital(${h.id})">Delete</button></td>
      </tr>
    `;
  });
}

document.getElementById("addHospitalForm")?.addEventListener("submit", async e => {
  e.preventDefault();
  const payload = {
    name: hname.value,
    address: haddress.value
  };
  await fetch(`${API_BASE}/api/hospitals`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  alert("Hospital added!");
  e.target.reset();
  loadHospitals();
});

async function deleteHospital(id) {
  if (!confirm("Delete this hospital?")) return;
  await fetch(`${API_BASE}/api/hospitals/${id}`, {method: "DELETE"});
  loadHospitals();
}
