import { createApp } from "vue";
import App from "./App.vue";
import router from "./utils/router.js";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js"; 
// bundle includes Popper + modal JS

createApp(App).use(router).mount("#app");
