import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Define the Product type to match the backend schema
export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: number;
  inventory_count: number;
  image_url: string | null;
  created_at: string;
}

export interface ProductCreate {
  name: string;
  description: string | null;
  price: number;
  inventory_count: number;
}

export const getProducts = async (): Promise<Product[]> => {
  const response = await axios.get(`${API_URL}/products/`);
  return response.data;
};

export const createProduct = async (product: ProductCreate): Promise<Product> => {
  const response = await axios.post(`${API_URL}/products/`, product);
  return response.data;
};
