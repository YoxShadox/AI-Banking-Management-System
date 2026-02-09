// Lightweight global JS for menu toggle and toasts
document.addEventListener('DOMContentLoaded', function(){
  // mobile menu toggle
  const toggles = document.querySelectorAll('[data-toggle="mobile-menu"]');
  toggles.forEach(t=> t.addEventListener('click', ()=>{
    document.documentElement.classList.toggle('mobile-menu-open');
  }));

  // simple toast function exposed globally
  window.showToast = function(message, type='info'){
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-6 right-6 bg-slate-800 text-white px-4 py-2 rounded shadow-lg';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(()=>{ toast.style.opacity = '0'; setTimeout(()=> toast.remove(),300); }, 3500);
  };
});