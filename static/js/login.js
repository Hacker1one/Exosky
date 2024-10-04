document.getElementById('login-form').addEventListener('submit', async function(event) {
  event.preventDefault(); // Prevent traditional form submission

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (!email || !password) {
      alert("Please enter both email and password.");
      return;
  }
  
  console.log('Login submitted', { email, password });

  try {
      const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password })
      });

      const result = await response.json();
      if (response.ok) {
          alert(result.message); 
          setTimeout(() => {
            window.location.href = '/home';}, 400);
      } else {
          alert(result.error);  
      }
  } catch (error) {
      console.error('Error during login:', error);
      alert('An error occurred. Please try again later.');
  }
});
