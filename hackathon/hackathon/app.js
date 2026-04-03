// Sahanak App - Logic
"use strict";

const App = {
    currentUser: null,
    currentScreen: 'home',
    currentLanguage: 'en',
    symptoms: [
        "Fever", "Cough", "Chest Pain", "Headache", "Fatigue", 
        "Shortness of Breath", "Nausea", "Vomiting", "Dizziness", 
        "Sore Throat", "Body Ache", "Loss of Appetite", "Rash", 
        "Abdominal Pain", "Joint Pain", "Cold/Runny Nose", 
        "Palpitations", "Blurred Vision"
    ],
    selectedSymptoms: new Set(),
    selectedTimeline: '1-3 hrs',
    history: [],
    
    translations: {
        en: {
            app_title: "Sahanak",
            tagline: "Your health, guided.",
            btn_login: "Login",
            btn_signup: "Sign Up",
            welcome: "Welcome Back",
            username: "Username",
            password: "Password",
            no_account: "Don't have an account?",
            join: "Join Sahanak",
            full_name: "Full Name",
            gender: "Gender",
            age: "Age",
            select: "Select...",
            location: "Location (City/Area)",
            allergies: "Known Allergies",
            history: "Previous Medical History",
            emergency_contacts: "Emergency Contacts",
            contact1: "1st Emergency Contact (Name & Number)",
            contact2: "2nd Emergency Contact",
            contact3: "3rd Emergency Contact",
            create_username: "Create Username",
            create_password: "Create Password",
            continue_symptoms: "Continue to Symptom Check →",
            exp_today: "What are you experiencing?",
            how_long: "How long have you had these?",
            other_symptoms: "Other symptoms?",
            assess: "Assess My Symptoms →",
            analyzing: "Analyzing...",
            panic: "PANIC: Call Ambulance & Contacts",
            possible_indicators: "Possible Indicators",
            rec_specialist: "Recommended Specialist",
            home_remedies: "Home Remedies",
            what_avoid: "What to Avoid",
            warning_signs: "Warning Signs",
            done: "Done",
            history_title: "Symptom History",
            no_history: "No history yet.",
            disclaimer: "Disclaimer: Sahanak is an AI awareness tool, not a medical professional. This is not a diagnosis. In case of emergency, call local emergency services immediately.",
            urgency_low: "Low",
            urgency_medium: "Medium",
            urgency_high: "High",
            panic_title: "🚨 Emergency Alert",
            panic_msg: "Notifying emergency services and your contacts...",
            close: "Close"
        },
        hi: {
            app_title: "सहनाक",
            tagline: "आपका स्वास्थ्य, हमारा मार्गदर्शन।",
            btn_login: "लॉगिन",
            btn_signup: "साइन अप",
            welcome: "आपका स्वागत है",
            username: "उपयोगकर्ता नाम",
            password: "पासवर्ड",
            no_account: "क्या आपका खाता नहीं है?",
            join: "सहनाक से जुड़ें",
            full_name: "पूरा नाम",
            gender: "लिंग",
            age: "आयु",
            select: "चुनें...",
            location: "स्थान (शहर/क्षेत्र)",
            allergies: "ज्ञात एलर्जी",
            history: "पिछली चिकित्सा जानकारी",
            emergency_contacts: "आपातकालीन संपर्क",
            contact1: "पहला आपातकालीन संपर्क (नाम और नंबर)",
            contact2: "दूसरा आपातकालीन संपर्क",
            contact3: "तीसरा आपातकालीन संपर्क",
            create_username: "उपयोगकर्ता नाम बनाएं",
            create_password: "पासवर्ड बनाएं",
            continue_symptoms: "लक्षण जांच के लिए जारी रखें →",
            exp_today: "आज आप क्या अनुभव कर रहे हैं?",
            how_long: "ये लक्षण कब से हैं?",
            other_symptoms: "अन्य लक्षण?",
            assess: "मेरे लक्षणों का आकलन करें →",
            analyzing: "विश्लेषण हो रहा है...",
            panic: "घबराएं नहीं: एम्बुलेंस और संपर्कों को कॉल करें",
            possible_indicators: "संभावित संकेत",
            rec_specialist: "अनुशंसित विशेषज्ञ",
            home_remedies: "घरेलू उपचार",
            what_avoid: "क्या न करें",
            warning_signs: "चेतावनी के संकेत",
            done: "हो गया",
            history_title: "लक्षणों का इतिहास",
            no_history: "अभी तक कोई इतिहास नहीं है।",
            disclaimer: "अस्वीकरण: सहनाक एक AI जागरूकता उपकरण है, चिकित्सा पेशेवर नहीं। यह निदान नहीं है। आपात स्थिति में, तुरंत स्थानीय आपातकालीन सेवाओं को कॉल करें।",
            urgency_low: "कम",
            urgency_medium: "मध्यम",
            urgency_high: "उच्च",
            panic_title: "🚨 आपातकालीन अलर्ट",
            panic_msg: "आपातकालीन सेवाओं और आपके संपर्कों को सूचित किया जा रहा है...",
            close: "बंद करें"
        },
        ma: {
            app_title: "सहनाक",
            tagline: "तुमचे आरोग्य, आमचे मार्गदर्शन.",
            btn_login: "लॉगिन",
            btn_signup: "साइन अप",
            welcome: "पुन्हा स्वागत आहे",
            username: "वापरकर्ता नाव",
            password: "पासवर्ड",
            no_account: "तुमचे खाते नाही का?",
            join: "सहनाक मध्ये सामील व्हा",
            full_name: "पूर्ण नाव",
            gender: "लिंग",
            age: "वय",
            select: "निवडा...",
            location: "ठिकाण (शहर/भाग)",
            allergies: "ज्ञात ऍलर्जी",
            history: "मागील वैद्यकीय माहिती",
            emergency_contacts: "आणीबाणीचे संपर्क",
            contact1: "पहिला आणीबाणीचा संपर्क (नाव आणि नंबर)",
            contact2: "दुसरा आणीबाणीचा संपर्क",
            contact3: "तिसरा आणीबाणीचा संपर्क",
            create_username: "वापरकर्ता नाव तयार करा",
            create_password: "पासवर्ड तयार करा",
            continue_symptoms: "लक्षण तपासण्यासाठी पुढे जा →",
            exp_today: "आज तुम्हाला काय जाणवत आहे?",
            how_long: "हे किती काळापासून होत आहे?",
            other_symptoms: "इतर लक्षणे?",
            assess: "माझ्या लक्षणांचे आकलन करा →",
            analyzing: "विश्लेषण करत आहे...",
            panic: "पॅनिक: रुग्णवाहिका आणि संपर्कांना कॉल करा",
            possible_indicators: "संभावित संकेत",
            rec_specialist: "शिफारस केलेले तज्ज्ञ",
            home_remedies: "घरगुती उपाय",
            what_avoid: "काय टाळावे",
            warning_signs: "धोक्याचे संकेत",
            done: "पूर्ण",
            history_title: "लक्षणांचा इतिहास",
            no_history: "अद्याप इतिहास नाही.",
            disclaimer: "अस्वीकरण: सहनाक एक AI जागरूकता साधन आहे, वैद्यकीय व्यावसायिक नाही. हे निदान नाही. आणीबाणीच्या परिस्थितीत, त्वरित स्थानिक आणीबाणी सेवांना कॉल करा.",
            urgency_low: "कमी",
            urgency_medium: "मध्यम",
            urgency_high: "उच्च",
            panic_title: "🚨 आणीबाणीचा इशारा",
            panic_msg: "आणीबाणी सेवा आणि तुमच्या संपर्कांना कळवत आहे...",
            close: "बंद करा"
        }
    },

    puneDoctors: {
        "Cardiologist": "Dr. Rahul Sawant (Jehangir Hospital)",
        "General Practitioner": "Dr. Amit Kulkarni (Aundh)",
        "Dermatologist": "Dr. Pradeep Kumari (Skin City)",
        "Orthopedic": "Dr. Hemant Wakankar (Deenanath Mangeshkar Hospital)",
        "Pediatrician": "Dr. Pramod Jog (Pune Station)",
        "Neurologist": "Dr. Rajas Deshpande (Ruby Hall Clinic)",
        "Pulmonologist": "Dr. Mahavir Modi (Ruby Hall)",
        "Gastroenterologist": "Dr. Parimal Lawate (Jehangir Hospital)",
        "Ent Specialist": "Dr. Samir Bhave (Poona Hospital)"
    },

    init() {
        this.container = document.getElementById('screen-container');
        this.nav = document.getElementById('main-nav');
        this.disclaimer = document.getElementById('global-disclaimer');
        this.langSelect = document.getElementById('lang-select');
        
        this.loadUser();
        this.render();
        this.bindGlobalEvents();
        this.applyTranslations();
    },

    loadUser() {
        const savedUser = localStorage.getItem('sahanak_user');
        if (savedUser) {
            this.currentUser = JSON.parse(savedUser);
            this.history = JSON.parse(localStorage.getItem(`sahanak_history_${this.currentUser.username}`) || '[]');
        }
    },

    saveUser(user) {
        localStorage.setItem('sahanak_user', JSON.stringify(user));
        this.currentUser = user;
        const users = JSON.parse(localStorage.getItem('sahanak_users') || '[]');
        if (!users.find(u => u.username === user.username)) {
            users.push(user);
            localStorage.setItem('sahanak_users', JSON.stringify(users));
        }
    },

    setLanguage(lang) {
        this.currentLanguage = lang;
        this.render();
        this.applyTranslations();
    },

    applyTranslations() {
        const t = this.translations[this.currentLanguage];
        
        // Static elements
        const set = (id, key) => { if(document.getElementById(id)) document.getElementById(id).textContent = t[key]; };
        const setHtml = (id, key) => { if(document.getElementById(id)) document.getElementById(id).innerHTML = t[key]; };
        
        set('txt-tagline', 'tagline');
        set('txt-disclaimer', 'disclaimer');
        set('panic-title', 'panic_title');
        set('panic-msg', 'panic_msg');
        set('btn-close-panic', 'close');

        // Nav
        if(this.currentScreen === 'home') {
            set('btn-goto-login', 'btn_login');
            set('btn-goto-signup', 'btn_signup');
        }

        if(this.currentScreen === 'login') {
            set('txt-welcome', 'welcome');
            set('lbl-username', 'username');
            set('lbl-password', 'password');
            set('btn-login', 'btn_login');
            set('txt-no-account', 'no_account');
            document.getElementById('link-signup').textContent = t['btn_signup'];
        }

        if(this.currentScreen === 'signup') {
            set('txt-join', 'join');
            set('lbl-name', 'full_name');
            set('lbl-gender', 'gender');
            set('lbl-age', 'age');
            set('opt-select', 'select');
            set('lbl-location', 'location');
            set('lbl-allergies', 'allergies');
            set('lbl-history', 'history');
            set('txt-emergency-title', 'emergency_contacts');
            set('lbl-contact1', 'contact1');
            // Use innerHTML to preserve the (optional) span
            const c2 = document.getElementById('lbl-contact2');
            if(c2) c2.innerHTML = `${t['contact2']} <span class="optional">(optional)</span>`;
            const c3 = document.getElementById('lbl-contact3');
            if(c3) c3.innerHTML = `${t['contact3']} <span class="optional">(optional)</span>`;
            set('lbl-create-user', 'create_username');
            set('lbl-create-pass', 'create_password');
            set('btn-signup-submit', 'continue_symptoms');
        }

        if(this.currentScreen === 'symptoms') {
            set('txt-exp-today', 'exp_today');
            set('txt-how-long', 'how_long');
            set('lbl-other', 'other_symptoms');
            set('btn-assess', 'assess');
        }

        if(this.currentScreen === 'results') {
            set('txt-panic', 'panic');
            set('txt-indicators', 'possible_indicators');
            set('txt-rec-specialist', 'rec_specialist');
            set('txt-home_remedies', 'home_remedies');
            set('txt-what-avoid', 'what_avoid');
            set('txt-warning-signs', 'warning_signs');
            set('btn-done', 'done');
        }

        if(this.currentScreen === 'history') {
            set('txt-history-title', 'history_title');
            set('history-empty', 'no_history');
        }
    },

    render() {
        this.container.innerHTML = '';
        const templateId = `tmpl-${this.currentScreen}`;
        const template = document.getElementById(templateId);
        if (!template) return;
        const clone = template.content.cloneNode(true);
        this.container.appendChild(clone);
        this.bindScreenEvents();
        this.updateNavVisibility();
        this.applyTranslations();
    },

    navigate(screen) {
        this.currentScreen = screen;
        this.render();
        window.scrollTo(0,0);
    },

    updateNavVisibility() {
        if (this.currentUser && !['home', 'login', 'signup'].includes(this.currentScreen)) {
            this.nav.classList.remove('hidden');
        } else {
            this.nav.classList.add('hidden');
        }
        if (this.currentScreen === 'results') {
            this.disclaimer.classList.remove('hidden');
        } else {
            this.disclaimer.classList.add('hidden');
        }
    },

    bindGlobalEvents() {
        document.getElementById('nav-home').addEventListener('click', () => this.navigate('symptoms'));
        document.getElementById('nav-history').addEventListener('click', () => this.navigate('history'));
        document.getElementById('nav-profile').addEventListener('click', () => {
             if(confirm("Logout?")) {
                 localStorage.removeItem('sahanak_user');
                 this.currentUser = null;
                 this.navigate('home');
             }
        });
        this.langSelect.addEventListener('change', (e) => this.setLanguage(e.target.value));
        document.getElementById('btn-close-panic').addEventListener('click', () => {
             document.getElementById('panic-modal').classList.add('hidden');
        });
    },

    bindScreenEvents() {
        if (this.currentScreen === 'home') {
            document.getElementById('btn-goto-login').addEventListener('click', () => this.navigate('login'));
            document.getElementById('btn-goto-signup').addEventListener('click', () => this.navigate('signup'));
        }

        if (this.currentScreen === 'login') {
            document.getElementById('form-login').addEventListener('submit', (e) => {
                e.preventDefault();
                const user = document.getElementById('login-username').value;
                const pass = document.getElementById('login-password').value;
                const users = JSON.parse(localStorage.getItem('sahanak_users') || '[]');
                const found = users.find(u => u.username === user && u.password === pass);
                if (found) { this.saveUser(found); this.navigate('symptoms'); }
                else { alert('Invalid credentials'); }
            });
            document.getElementById('link-signup').addEventListener('click', (e) => {
                e.preventDefault(); this.navigate('signup');
            });
        }

        if (this.currentScreen === 'signup') {
            document.getElementById('form-signup').addEventListener('submit', (e) => {
                e.preventDefault();
                const newUser = {
                    name: document.getElementById('signup-name').value,
                    gender: document.getElementById('signup-gender').value,
                    age: document.getElementById('signup-age').value,
                    location: document.getElementById('signup-location').value,
                    allergies: document.getElementById('signup-allergies').value || 'None',
                    history: document.getElementById('signup-history').value || 'None',
                    username: document.getElementById('signup-username').value,
                    password: document.getElementById('signup-password').value,
                    contacts: [
                        document.getElementById('signup-contact1').value,
                        document.getElementById('signup-contact2').value,
                        document.getElementById('signup-contact3').value
                    ]
                };
                this.saveUser(newUser); this.navigate('symptoms');
            });
        }

        if (this.currentScreen === 'symptoms') {
            const chipContainer = document.getElementById('symptom-chips');
            this.symptoms.forEach(s => {
                const chip = document.createElement('div');
                chip.className = `chip ${this.selectedSymptoms.has(s) ? 'selected' : ''}`;
                chip.textContent = s;
                chip.addEventListener('click', () => {
                    if (this.selectedSymptoms.has(s)) { this.selectedSymptoms.delete(s); chip.classList.remove('selected'); }
                    else { this.selectedSymptoms.add(s); chip.classList.add('selected'); }
                });
                chipContainer.appendChild(chip);
            });

            document.getElementById('btn-assess').addEventListener('click', () => {
                const timeline = document.querySelector('input[name="timeline"]:checked').value;
                this.selectedTimeline = timeline;
                const others = document.getElementById('symptom-other').value;
                this.assessSymptoms([...this.selectedSymptoms], others);
            });
        }

        if (this.currentScreen === 'results') {
            document.getElementById('btn-done').addEventListener('click', () => this.navigate('symptoms'));
            document.getElementById('btn-panic').addEventListener('click', () => this.triggerPanic());
        }

        if (this.currentScreen === 'history') { this.renderHistory(); }
    },

    async assessSymptoms(symptoms, extra) {
        if (symptoms.length === 0 && !extra) { alert('Please select at least one symptom.'); return; }
        const btn = document.getElementById('btn-assess');
        btn.disabled = true;
        btn.textContent = this.translations[this.currentLanguage].analyzing;
        try {
            const assessment = await this.callClaudeAPI(symptoms, extra);
            this.saveToHistory(assessment);
            this.navigate('results');
            this.fillResults(assessment);
        } catch (e) { alert('Error: ' + e.message); }
        finally { btn.disabled = false; btn.textContent = this.translations[this.currentLanguage].assess; }
    },

    async callClaudeAPI(symptoms, extra) {
        // Updated AI prompt logic for duration and language
        const mock = {
            urgency: symptoms.includes('Chest Pain') || symptoms.includes('Shortness of Breath') ? 'High' : (symptoms.length > 2 ? 'Medium' : 'Low'),
            urgencyLevel: symptoms.includes('Chest Pain') ? 'RED' : (symptoms.length > 2 ? 'YELLOW' : 'GREEN'),
            message: `Assessment for ${this.currentUser.name}. Duration: ${this.selectedTimeline}.`,
            conditions: ["Possible Indicator 1", "Possible Indicator 2"],
            specialist: symptoms.includes('Chest Pain') ? "Cardiologist" : "General Practitioner",
            remedies: ["Rest", "Hydration"],
            avoid: ["Stress", "Cold air"],
            warningSigns: "If pain radiates to arm or jaw."
        };
        return new Promise(res => setTimeout(() => res(mock), 1500));
    },

    fillResults(data) {
        const card = document.getElementById('result-status-card');
        const t = this.translations[this.currentLanguage];
        
        let colorClass = 'green';
        let label = t.urgency_low;
        if(data.urgency === 'High') { colorClass = 'red'; label = t.urgency_high; }
        else if(data.urgency === 'Medium') { colorClass = 'yellow'; label = t.urgency_medium; }

        card.className = `urgency-card ${colorClass}`;
        card.innerHTML = `<h2>${label}</h2>`;

        const panicBtn = document.getElementById('btn-panic');
        if(data.urgency === 'High') { panicBtn.classList.remove('hidden'); }
        else { panicBtn.classList.add('hidden'); }

        document.getElementById('result-message').textContent = data.message;
        document.getElementById('res-conditions').textContent = data.conditions.join(', ');
        const doctor = this.puneDoctors[data.specialist] || `Dr. Pune Specialist for ${data.specialist}`;
        document.getElementById('res-specialist').textContent = `${data.specialist}: ${doctor}`;
        
        const remedyList = document.getElementById('res-remedies');
        remedyList.innerHTML = '';
        data.remedies.forEach(r => { remedyList.innerHTML += `<li>${r}</li>`; });

        const avoidList = document.getElementById('res-avoid');
        avoidList.innerHTML = '';
        data.avoid.forEach(a => { avoidList.innerHTML += `<li>${a}</li>`; });

        document.getElementById('res-warning').textContent = data.warningSigns;
    },

    triggerPanic() {
        document.getElementById('panic-modal').classList.remove('hidden');
        const contacts = this.currentUser.contacts || [];
        document.getElementById('ping-1').textContent = `Contact 1: ${contacts[0] || 'Unknown'} - Notified`;
        document.getElementById('ping-2').textContent = `Contact 2: ${contacts[1] || 'Unknown'} - Notified`;
        document.getElementById('ping-3').textContent = `Contact 3: ${contacts[2] || 'Unknown'} - Notified`;
    },

    saveToHistory(result) {
        const item = {
            date: new Date().toLocaleString(),
            urgency: result.urgency,
            symptoms: [...this.selectedSymptoms]
        };
        this.history.unshift(item);
        localStorage.setItem(`sahanak_history_${this.currentUser.username}`, JSON.stringify(this.history));
    },

    renderHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        if (this.history.length === 0) { document.getElementById('history-empty').classList.remove('hidden'); return; }
        document.getElementById('history-empty').classList.add('hidden');
        this.history.forEach(item => {
            let color = 'green';
            if(item.urgency === 'High') color = 'red';
            if(item.urgency === 'Medium') color = 'yellow';
            list.innerHTML += `<div class="history-item"><div><strong>${item.date}</strong><p>${item.symptoms.join(', ')}</p></div><div class="badge ${color}"></div></div>`;
        });
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
