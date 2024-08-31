// setTimeout(function() {
//     // تغییر مسیر به صفحه دیگری
//     window.location.href = 'input page/input.html'; // جایگزین با مسیر صفحه هدف خود
// }, 5000);
        // تابع برای هدایت به صفحه جدید پس از ۵ ثانیه
        function redirectToInput() {
            setTimeout(function() {
                window.location.href = 'http://127.0.0.1:5500/input%20page/input.html';
            }, 5000); // ۵۰۰۰ میلی‌ثانیه = ۵ ثانیه
        }

        // اجرای تابع هنگام بارگذاری صفحه
        window.onload = redirectToInput;
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                window.location.href = "/";  // Redirect to home page after 3 seconds
            }, 3000);
        });