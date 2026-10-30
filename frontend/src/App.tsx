// Just a standard component, nothing fancy here.


import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

export default function App() {
  return (
    // ThemeProvider gives all components access to dark/light mode state
    <ThemeProvider>
      {/* AuthProvider gives all components access to login/user state */}
      <AuthProvider>
        {/* RouterProvider handles the URLs and which pages to show */}
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>
  );
}
