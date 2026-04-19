import { ref } from "vue";

export const isLoggedIn = ref(!!localStorage.getItem("token"));
export const userRole = ref(localStorage.getItem("role") || null);

export function login(token, role) {
    localStorage.setItem("token", token);
    localStorage.setItem("role", role);

    isLoggedIn.value = true;
    userRole.value = role;
}

export function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    
    isLoggedIn.value = false;
    userRole.value = null;
}
