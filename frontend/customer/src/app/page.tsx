"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";

type Shipment = {
  id: string;
  sender: string;
  senderPhone: string;
  receiver: string;
  receiverPhone: string;
  pickup: string;
  delivery: string;
  description: string;
  weight: number;
  deliveryType: string;
  payment: string;
  price: number;
  status: string;
  date: string;
};

type User = {
  name: string;
  email: string;
  password: string;
};

type Page = "dashboard" | "booking" | "tracking" | "shipments" | "profile";

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [registerMode, setRegisterMode] = useState(false);
  const [activePage, setActivePage] = useState<Page>("dashboard");
  const [message, setMessage] = useState("");
  const [messageError, setMessageError] = useState(false);

  const [trackingId, setTrackingId] = useState("");
  const [trackingResult, setTrackingResult] = useState<Shipment | null>(null);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [users, setUsers] = useState<User[]>([
    {
      name: "Demo Customer",
      email: "customer@gmail.com",
      password: "123456",
    },
  ]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const savedShipments = localStorage.getItem("courierShipments");
      const savedUsers = localStorage.getItem("courierUsers");

      if (savedShipments) setShipments(JSON.parse(savedShipments));
      if (savedUsers) setUsers(JSON.parse(savedUsers));
    } catch {
      console.log("Could not load saved data.");
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready) {
      localStorage.setItem("courierShipments", JSON.stringify(shipments));
      localStorage.setItem("courierUsers", JSON.stringify(users));
    }
  }, [shipments, users, ready]);

  const processingCount = shipments.filter(
    (s) => s.status === "Processing"
  ).length;

  const deliveredCount = shipments.filter(
    (s) => s.status === "Delivered"
  ).length;

  function showMessage(text: string, error = false) {
    setMessage(text);
    setMessageError(error);
  }

  function handleLogin(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const user = users.find(
      (u) =>
        u.email.toLowerCase() === email.trim().toLowerCase() &&
        u.password === password
    );

    if (!user) {
      showMessage("Invalid email or password.", true);
      return;
    }

    setCustomerName(user.name);
    setEmail(user.email);
    setLoggedIn(true);
    setMessage("");
  }

  function handleRegister(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (users.some((u) => u.email.toLowerCase() === email.trim().toLowerCase())) {
      showMessage("This email is already registered. Please log in.", true);
      return;
    }

    const newUser = {
      name: customerName.trim(),
      email: email.trim(),
      password,
    };

    if (!newUser.name || password.length < 6 || !email.includes("@")) {
      showMessage("Enter a valid name, email and password of at least 6 characters.", true);
      return;
    }

    setUsers([...users, newUser]);
    setCustomerName(newUser.name);
    setEmail(newUser.email);
    setLoggedIn(true);
    setRegisterMode(false);
    showMessage("Your account was created successfully!");
  }

  function handleBooking(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const form = e.currentTarget;
    const data = new FormData(form);

    const weight = Number(data.get("weight"));
    const deliveryType = String(data.get("deliveryType"));
    const price = Math.round(
      weight * (deliveryType === "Express" ? 150 : 80)
    );

    const newShipment: Shipment = {
      id: "QC" + Date.now().toString().slice(-10),
      sender: String(data.get("sender")),
      senderPhone: String(data.get("senderPhone")),
      receiver: String(data.get("receiver")),
      receiverPhone: String(data.get("receiverPhone")),
      pickup: String(data.get("pickup")),
      delivery: String(data.get("delivery")),
      description: String(data.get("description")),
      weight,
      deliveryType,
      payment: String(data.get("payment")),
      price,
      status: "Processing",
      date: new Date().toLocaleDateString("en-IN"),
    };

    setShipments((previous) => [newShipment, ...previous]);
    showMessage("Courier booked successfully! Your tracking ID is " + newShipment.id);
    form.reset();
    setActivePage("booking");
  }

  function handleTracking(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const found = shipments.find(
      (s) => s.id.toLowerCase() === trackingId.trim().toLowerCase()
    );

    setTrackingResult(found || null);

    if (found) {
      showMessage("Shipment found successfully!");
    } else {
      showMessage("Shipment not found. Please check your tracking ID.", true);
    }
  }

  function logout() {
    setLoggedIn(false);
    setPassword("");
    setActivePage("dashboard");
    setMessage("");
    setTrackingResult(null);
  }

  const navigation: { id: Page; label: string; icon: string }[] = [
    { id: "dashboard", label: "Dashboard", icon: "⌂" },
    { id: "booking", label: "Book a Courier", icon: "＋" },
    { id: "tracking", label: "Track Shipment", icon: "⌕" },
    { id: "shipments", label: "My Shipments", icon: "▤" },
    { id: "profile", label: "My Profile", icon: "♙" },
  ];

  if (!loggedIn) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-100 to-slate-200 p-5">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
          <div className="mb-7 text-center">
            <div className="mb-3 text-5xl">📦</div>
            <h1 className="text-3xl font-extrabold text-blue-800">
              QuickCourier
            </h1>
            <p className="mt-2 text-gray-500">Customer Portal</p>
          </div>

          <h2 className="mb-5 text-xl font-bold text-gray-800">
            {registerMode ? "Create Your Account" : "Customer Login"}
          </h2>

          <form
            onSubmit={registerMode ? handleRegister : handleLogin}
            className="space-y-4"
          >
            {registerMode && (
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <input
                  required
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full rounded-lg border p-3 text-gray-800"
                  placeholder="Enter your full name"
                />
              </div>
            )}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border p-3 text-gray-800"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border p-3 text-gray-800"
                placeholder="Minimum 6 characters"
              />
            </div>

            {message && (
              <p className={`text-sm ${messageError ? "text-red-600" : "text-green-700"}`}>
                {message}
              </p>
            )}

            <button className="w-full rounded-lg bg-blue-700 p-3 font-semibold text-white hover:bg-blue-800">
              {registerMode ? "Create Account" : "Login"}
            </button>
          </form>

          <button
            onClick={() => {
              setRegisterMode(!registerMode);
              setMessage("");
            }}
            className="mt-5 w-full text-sm font-medium text-blue-700 hover:underline"
          >
            {registerMode
              ? "Already have an account? Login"
              : "New customer? Create an account"}
          </button>

          <div className="mt-6 rounded-lg bg-blue-50 p-3 text-center text-sm text-gray-600">
            Demo login
            <br />
            Email: customer@gmail.com
            <br />
            Password: 123456
          </div>
        </div>
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="flex flex-wrap items-center justify-between gap-3 bg-blue-800 px-5 py-4 text-white shadow">
        <div>
          <h1 className="text-2xl font-extrabold">📦 QuickCourier</h1>
          <p className="text-xs text-blue-100">Customer Portal</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="hidden text-sm sm:block">{email}</span>
          <button
            onClick={logout}
            className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-blue-800 hover:bg-blue-100"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="flex min-h-[88vh] flex-col md:flex-row">
        <aside className="w-full bg-white p-4 shadow md:w-64">
          <p className="mb-4 px-3 text-xs font-bold uppercase tracking-wider text-gray-400">
            Main Menu
          </p>
          <nav className="grid grid-cols-2 gap-2 md:grid-cols-1">
            {navigation.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setActivePage(item.id);
                  setMessage("");
                  setTrackingResult(null);
                }}
                className={`rounded-lg p-3 text-left font-medium transition ${
                  activePage === item.id
                    ? "bg-blue-700 text-white"
                    : "text-gray-700 hover:bg-blue-50"
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>
          <div className="mt-8 hidden rounded-xl bg-blue-50 p-4 md:block">
            <p className="font-semibold text-blue-800">Need help?</p>
            <p className="mt-1 text-sm text-gray-600">
              Contact our customer support for assistance with your shipment.
            </p>
          </div>
        </aside>

        <main className="min-w-0 flex-1 p-5 md:p-8">
          {activePage === "dashboard" && (
            <>
              <div className="mb-7">
                <h2 className="text-3xl font-bold text-gray-800">
                  Welcome, {customerName || "Customer"}!
                </h2>
                <p className="mt-2 text-gray-500">
                  Manage your courier bookings and deliveries from here.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {[
                  { title: "Total Shipments", value: shipments.length, icon: "📦" },
                  { title: "Processing", value: processingCount, icon: "🚚" },
                  { title: "Delivered", value: deliveredCount, icon: "✅" },
                ].map((item) => (
                  <div key={item.title} className="rounded-xl bg-white p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-500">{item.title}</p>
                      <span className="text-2xl">{item.icon}</span>
                    </div>
                    <p className="mt-4 text-4xl font-bold text-blue-700">
                      {item.value}
                    </p>
                  </div>
                ))}
              </div>

              <h3 className="mb-4 mt-9 text-xl font-bold text-gray-800">
                Quick Actions
              </h3>
              <div className="grid gap-5 md:grid-cols-2">
                <button
                  onClick={() => setActivePage("booking")}
                  className="rounded-xl border border-gray-100 bg-white p-7 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-md"
                >
                  <span className="text-3xl">📦</span>
                  <h4 className="mt-3 text-xl font-bold text-blue-800">
                    Book a Courier
                  </h4>
                  <p className="mt-2 text-gray-500">
                    Schedule a new parcel pickup and delivery.
                  </p>
                </button>
                <button
                  onClick={() => setActivePage("tracking")}
                  className="rounded-xl border border-gray-100 bg-white p-7 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-md"
                >
                  <span className="text-3xl">🔍</span>
                  <h4 className="mt-3 text-xl font-bold text-blue-800">
                    Track Shipment
                  </h4>
                  <p className="mt-2 text-gray-500">
                    Check the current status of your parcel.
                  </p>
                </button>
              </div>

              <div className="mt-8 rounded-xl bg-white p-5 shadow-sm">
                <h3 className="mb-3 text-lg font-bold text-gray-800">
                  Recent Shipments
                </h3>
                {shipments.length === 0 ? (
                  <p className="text-gray-500">You have no shipments yet.</p>
                ) : (
                  <div className="space-y-3">
                    {shipments.slice(0, 3).map((s) => (
                      <div key={s.id} className="flex flex-wrap justify-between gap-2 border-b pb-3">
                        <div>
                          <p className="font-semibold text-gray-800">{s.id}</p>
                          <p className="text-sm text-gray-500">To: {s.receiver}</p>
                        </div>
                        <span className="h-fit rounded-full bg-amber-100 px-3 py-1 text-sm text-amber-800">
                          {s.status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          {activePage === "booking" && (
            <>
              <h2 className="mb-2 text-3xl font-bold text-gray-800">
                Book a Courier
              </h2>
              <p className="mb-6 text-gray-500">
                Enter the sender, receiver and parcel information.
              </p>

              <form onSubmit={handleBooking} className="max-w-4xl space-y-6">
                <section className="rounded-xl bg-white p-5 shadow-sm md:p-7">
                  <h3 className="mb-5 border-b pb-3 text-lg font-bold text-blue-800">
                    Sender Details
                  </h3>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Sender Name *
                      </label>
                      <input name="sender" required className="w-full rounded-lg border p-3 text-gray-800" placeholder="Sender full name" />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Sender Phone *
                      </label>
                      <input name="senderPhone" type="tel" required pattern="[0-9]{10}" title="Enter a 10-digit phone number" className="w-full rounded-lg border p-3 text-gray-800" placeholder="10-digit mobile number" />
                    </div>
                    <div className="md:col-span-2">
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Pickup Address *
                      </label>
                      <textarea name="pickup" required rows={2} className="w-full rounded-lg border p-3 text-gray-800" placeholder="Complete pickup address" />
                    </div>
                  </div>
                </section>

                <section className="rounded-xl bg-white p-5 shadow-sm md:p-7">
                  <h3 className="mb-5 border-b pb-3 text-lg font-bold text-blue-800">
                    Receiver Details
                  </h3>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Receiver Name *
                      </label>
                      <input name="receiver" required className="w-full rounded-lg border p-3 text-gray-800" placeholder="Receiver full name" />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Receiver Phone *
                      </label>
                      <input name="receiverPhone" type="tel" required pattern="[0-9]{10}" title="Enter a 10-digit phone number" className="w-full rounded-lg border p-3 text-gray-800" placeholder="10-digit mobile number" />
                    </div>
                    <div className="md:col-span-2">
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Delivery Address *
                      </label>
                      <textarea name="delivery" required rows={2} className="w-full rounded-lg border p-3 text-gray-800" placeholder="Complete delivery address" />
                    </div>
                  </div>
                </section>

                <section className="rounded-xl bg-white p-5 shadow-sm md:p-7">
                  <h3 className="mb-5 border-b pb-3 text-lg font-bold text-blue-800">
                    Parcel Details
                  </h3>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Parcel Description *
                      </label>
                      <input name="description" required className="w-full rounded-lg border p-3 text-gray-800" placeholder="Example: Books, clothes" />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Weight (kg) *
                      </label>
                      <input name="weight" type="number" min="0.1" max="100" step="0.1" required className="w-full rounded-lg border p-3 text-gray-800" placeholder="Example: 2" />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Delivery Type *
                      </label>
                      <select name="deliveryType" required className="w-full rounded-lg border p-3 text-gray-800">
                        <option value="Standard">Standard Delivery</option>
                        <option value="Express">Express Delivery</option>
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">
                        Payment Method *
                      </label>
                      <select name="payment" required className="w-full rounded-lg border p-3 text-gray-800">
                        <option value="Cash on Delivery">Cash on Delivery</option>
                        <option value="Online Payment">Online Payment (demo only)</option>
                        <option value="Pay at Pickup">Pay at Pickup</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-5 rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
                    <strong>Estimated pricing (demo):</strong> Standard ₹80 per kg; Express ₹150 per kg. Final charges may differ.
                  </div>
                </section>

                <button className="w-full rounded-lg bg-blue-700 px-6 py-4 font-bold text-white shadow hover:bg-blue-800 md:w-auto">
                  Confirm Courier Booking
                </button>
              </form>
            </>
          )}

          {activePage === "tracking" && (
            <>
              <h2 className="mb-2 text-3xl font-bold text-gray-800">
                Track Shipment
              </h2>
              <p className="mb-6 text-gray-500">
                Enter your tracking ID to check your parcel status.
              </p>
              <form onSubmit={handleTracking} className="max-w-xl rounded-xl bg-white p-6 shadow-sm">
                <label className="mb-2 block font-medium text-gray-700">
                  Tracking ID
                </label>
                <input
                  value={trackingId}
                  onChange={(e) => setTrackingId(e.target.value)}
                  required
                  className="mb-4 w-full rounded-lg border p-3 text-gray-800"
                  placeholder="Example: QC1234567890"
                />
                <button className="rounded-lg bg-blue-700 px-6 py-3 font-semibold text-white hover:bg-blue-800">
                  Track Now
                </button>
              </form>

              {trackingResult && (
                <div className="mt-6 max-w-xl rounded-xl bg-white p-6 shadow-sm">
                  <h3 className="mb-4 text-xl font-bold text-blue-800">
                    Shipment Details
                  </h3>
                  <p className="mb-2 text-gray-700"><strong>Tracking ID:</strong> {trackingResult.id}</p>
                  <p className="mb-2 text-gray-700"><strong>Receiver:</strong> {trackingResult.receiver}</p>
                  <p className="mb-2 text-gray-700"><strong>Delivery Address:</strong> {trackingResult.delivery}</p>
                  <p className="mb-2 text-gray-700"><strong>Delivery Type:</strong> {trackingResult.deliveryType}</p>
                  <p className="mb-2 text-gray-700"><strong>Booking Date:</strong> {trackingResult.date}</p>
                  <p className="mt-4 inline-block rounded-full bg-amber-100 px-4 py-2 font-semibold text-amber-800">
                    Status: {trackingResult.status}
                  </p>
                </div>
              )}
            </>
          )}

          {activePage === "shipments" && (
            <>
              <h2 className="mb-2 text-3xl font-bold text-gray-800">
                My Shipments
              </h2>
              <p className="mb-6 text-gray-500">
                View all your courier bookings.
              </p>
              <div className="overflow-x-auto rounded-xl bg-white p-5 shadow-sm">
                {shipments.length === 0 ? (
                  <p className="py-5 text-gray-500">No shipments booked yet.</p>
                ) : (
                  <table className="w-full min-w-[750px] text-left text-sm">
                    <thead>
                      <tr className="border-b text-gray-500">
                        <th className="p-3">Tracking ID</th>
                        <th className="p-3">Receiver</th>
                        <th className="p-3">Delivery Type</th>
                        <th className="p-3">Price</th>
                        <th className="p-3">Date</th>
                        <th className="p-3">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {shipments.map((s) => (
                        <tr key={s.id} className="border-b text-gray-700">
                          <td className="p-3 font-semibold">{s.id}</td>
                          <td className="p-3">{s.receiver}</td>
                          <td className="p-3">{s.deliveryType}</td>
                          <td className="p-3">₹{s.price}</td>
                          <td className="p-3">{s.date}</td>
                          <td className="p-3">
                            <span className="rounded-full bg-amber-100 px-3 py-1 text-amber-800">
                              {s.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          )}

          {activePage === "profile" && (
            <>
              <h2 className="mb-6 text-3xl font-bold text-gray-800">
                My Profile
              </h2>
              <div className="max-w-xl rounded-xl bg-white p-7 shadow-sm">
                <div className="mb-5 text-5xl">👤</div>
                <p className="mb-4 text-gray-500">Customer Account Information</p>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-500">Customer Name</p>
                    <p className="font-semibold text-gray-800">{customerName || "Demo Customer"}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Email Address</p>
                    <p className="font-semibold text-gray-800">{email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Account Type</p>
                    <p className="font-semibold text-gray-800">Customer</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Total Bookings</p>
                    <p className="font-semibold text-gray-800">{shipments.length}</p>
                  </div>
                </div>
              </div>
            </>
          )}

          {message && (
            <div className={`mt-6 max-w-4xl rounded-lg p-4 font-medium ${
              messageError
                ? "bg-red-50 text-red-700"
                : "bg-green-50 text-green-800"
            }`}>
              {message}
            </div>
          )}

          <footer className="mt-10 border-t pt-5 text-center text-sm text-gray-400">
            © 2026 QuickCourier Customer Portal
          </footer>
        </main>
      </div>
    </div>
  );
}