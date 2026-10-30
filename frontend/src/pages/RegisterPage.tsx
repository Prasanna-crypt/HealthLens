// Just a standard component, nothing fancy here.

import React from 'react';
import { RegisterForm } from '../components/auth/RegisterForm';

export const RegisterPage: React.FC = () => {
  return (
    // Full screen container with background styling
    <div className="min-h-screen flex items-center justify-center bg-transparent p-4">
      {/* Decorative blurred background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-primary-200/30 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] bg-accent-400/20 rounded-full blur-3xl"></div>
      </div>
      
      {/* The actual form component */}
      <div className="z-10 w-full max-w-md animate-fade-in">
        <RegisterForm />
      </div>
    </div>
  );
};
