import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const PrivateRoute = () => {
  // ここを 'token' に指定します
  const token = localStorage.getItem('token');

  return token ? <Outlet /> : <Navigate to="/signin" />;
};

export default PrivateRoute;