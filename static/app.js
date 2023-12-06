document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const loginError = document.getElementById("login-error");
    const logoutButton = document.getElementById("logout-button"); // Tambahkan ini

    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent the form from submitting

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            // Send a POST request to the server for login
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `email=${email}&password=${password}`,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to the base.html page upon successful login
                    window.location.href = "/base";
                } else {
                    // Display login error message
                    loginError.innerHTML = "Login gagal. Email atau password salah.";
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            // Send a GET request to the server for logout
            fetch('/logout', {
                method: 'GET'
            })
            .then(response => {
                // Redirect to the login page upon successful logout
                window.location.href = "/login";
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const signupForm = document.getElementById("signup-form");
    const signupError = document.getElementById("signup-error");

    if (signupForm) {
        signupForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Hindari pengiriman formulir

            const usernameInput = document.getElementById("username").value;
            const emailInput = document.getElementById("email").value;
            const passwordInput = document.getElementById("password").value;

            fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${usernameInput}&email=${emailInput}&password=${passwordInput}`,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Registrasi berhasil
                    alert('Registrasi berhasil! Silakan login.');
                    window.location.href = '/login'; // Arahkan pengguna ke halaman login
                } else {
                    // Registrasi gagal
                    signupError.textContent = data.message;
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});

class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
    }

    addQuestion(question) {
        var inputField = this.args.chatBox.querySelector('.chatbox__footer input');
        inputField.value = question;
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if (this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                let msg2 = { name: "HalalBot", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(chatbox)
                textField.value = ''

            }).catch((error) => {
                console.error('Error:', error);
                this.updateChatText(chatbox)
                textField.value = ''
            });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function (item, index) {
            if (item.name === "HalalBot") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }

    likeMessage(index) {
        // Handle liking the message at the specified index
        console.log(`Liked message at index ${index}`);
    }

    dislikeMessage(index) {
        // Handle disliking the message at the specified index
        console.log(`Disliked message at index ${index}`);
    }

    // Fungsi untuk mendapatkan dan menampilkan log chat admin
    fetchAdminChatLogs() {
        fetch('/admin/chat_logs') // Ganti dengan endpoint yang sesuai di Flask app Anda
            .then(response => response.json())
            .then(data => {
                this.updateAdminChatLogs(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    updateAdminChatLogs(data) {
        const logTableBody = document.getElementById('log-table-body');
        logTableBody.innerHTML = ""; // Clear previous content

        // Iterate through chat logs and append to the table
        data.logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${log.username}</td>
                <td>${log.timestamp}</td>
                <td>${log.message}</td>
            `;
            logTableBody.appendChild(row);
        });
    }

    displayAdminChatLogs() {
        const logTable = document.getElementById('log-table'); // Ganti dengan ID yang sesuai pada halaman edit.html
        const logTableBody = logTable.getElementsByTagName('tbody')[0];

        this.messages.forEach(log => {
            const row = logTableBody.insertRow(-1);
            const cell1 = row.insertCell(0);
            const cell2 = row.insertCell(1);
            const cell3 = row.insertCell(2);

            cell1.textContent = log.name;
            cell2.textContent = log.timestamp;
            cell3.textContent = log.message;
        });
    }
}

// Fetch and display admin chat logs
function fetchAdminChatLogs() {
    fetch('/admin/chat_logs')
        .then(response => response.json())
        .then(data => {
            const chatbox = new Chatbox();
            chatbox.updateAdminChatLogs(data);
            chatbox.displayAdminChatLogs(); // Tambahkan ini
        })
        .catch(error => {
            console.error('Error fetching chat logs:', error);
        });
}

const chatbox = new Chatbox();
chatbox.display();
fetchAdminChatLogs();

function redirectToNews(newsLink) {
    window.location.href = newsLink;
}

function initMap() {
    // Koordinat BPJPH (latitude dan longitude)
    var bpjphLocation = { lat: -6.2901396, lng: 106.886238 };

    // Membuat peta dan menentukan lokasinya
    var map = new google.maps.Map(document.getElementById("map"), {
        center: bpjphLocation,
        zoom: 15, // Zoom level (sesuaikan dengan kebutuhan Anda)
    });

    // Menambahkan penanda pada lokasi BPJPH
    var marker = new google.maps.Marker({
        position: bpjphLocation,
        map: map,
        title: "Badan Penyelenggara Jaminan Produk Halal (BPJPH)",
    });
}

// Ambil elemen-elemen yang diperlukan
const userNameElement = document.getElementById("userName");
const userMenuElement = document.getElementById("userMenu");
const signupForm = document.getElementById("signup-form");  // Tambahkan elemen form

// Fungsi untuk mengubah teks "Halo, (Nama User)"
function updateUserName(namaUser) {
    userNameElement.textContent = `Halo, ${namaUser}`;
}

// Tambahkan event listener untuk form saat pengguna mengirimkan formulir
signupForm.addEventListener("submit", function (event) {
    event.preventDefault(); // Hindari pengiriman formulir

    // Dapatkan nilai input dari elemen username
    const usernameInput = document.getElementById("username");
    const newNamaUser = usernameInput.value;

    // Perbarui namaUser dengan nama pengguna yang baru
    namaUser = newNamaUser;

    // Panggil fungsi untuk mengatur nama pengguna
    updateUserName(namaUser);
});

document.addEventListener('DOMContentLoaded', function() {
    fetch('/edit')
        .then(response => response.json())
        .then(data => loadIntentsData(data.intents))
        .catch(error => console.error('Error fetching intents:', error));

    // Inisialisasi DataTable untuk tabel intents
    $(document).ready( function () {
        var table = $('#intents-table').DataTable({
            paging: true, // Aktifkan paginasi
            pageLength: 5 // Tentukan jumlah baris per halaman
        });

        // Load data intents setelah tabel diinisialisasi
        fetch('/edit')
            .then(response => response.json())
            .then(data => loadIntentsData(data.intents, table))
            .catch(error => console.error('Error fetching intents:', error));
    });

    fetch('/api/admin/chat_logs')
        .then(response => response.json())
        .then(data => loadChatLogs(data.logs))
        .catch(error => console.error('Error fetching chat logs:', error));
});

function loadIntentsData(intentsData, table) {
    table.clear(); // Bersihkan data yang sudah ada

    intentsData.forEach(function (intent) {
        table.row.add([intent.tag, intent.patterns.join(', '), intent.responses.join(', ')]).draw();
    });
}

function loadChatLogs(chatLogs) {
    var tableBody = document.getElementById('log-table-body');
    tableBody.innerHTML = ''; // Bersihkan konten tabel sebelum menambahkan data baru

    chatLogs.forEach(function(log) {
        var row = tableBody.insertRow();
        var usernameCell = row.insertCell(0);
        var timestampCell = row.insertCell(1);
        var questionCell = row.insertCell(2);

        usernameCell.innerHTML = log.username;
        timestampCell.innerHTML = log.timestamp;
        questionCell.innerHTML = log.question;
    });
}