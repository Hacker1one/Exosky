document.getElementById('signup-form').addEventListener('submit', async function(event) {
  event.preventDefault(); // Prevent traditional form submission

  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;

  if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
  }

  console.log('Sign up submitted', { name, email, password });

  try {
      const response = await fetch('http://127.0.0.1:5000/signup', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name, email, password }) 
      });

      const result = await response.json();
      
      if (response.ok) {
          alert(result.message); 
          setTimeout(() => {
            window.location.href = '/login';}, 1000);
      } else {
          alert(result.error); 
      }
  } catch (error) {
      console.error('Error during sign-up:', error);
      alert('An error occurred. Please try again later.');
  }
});
