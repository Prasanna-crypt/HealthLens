// Just a standard component, nothing fancy here.

import React, { createContext, useContext, useState, useEffect } from 'react';

// Defines the data available in the ThemeContext
interface ThemeContextType {
  theme: 'light' | 'dark'; // Current theme
  toggleTheme: () => void; // Function to switch themes
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize theme based on saved preference or system preference
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('healthlens_theme');
    if (saved === 'light' || saved === 'dark') return saved;
    // Fall back to OS preference if nothing is saved
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  // Whenever the theme changes, update local storage and the HTML class
  useEffect(() => {
    localStorage.setItem('healthlens_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Helper to switch between light and dark
  const toggleTheme = () => setTheme(t => (t === 'light' ? 'dark' : 'light'));

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to easily use the ThemeContext in any component
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within a ThemeProvider');
  return context;
};
