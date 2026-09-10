import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

// Client-side demo fallback generator when backend API is offline
const generateDemoResults = (query) => {
  const q = query.toLowerCase();
  let basePrice = 79900;
  let modelName = query;
  
  if (q.includes('iphone')) {
    modelName = q.includes('16') ? 'Apple iPhone 16 (128 GB)' : 'Apple iPhone 15 (128 GB)';
    basePrice = 79900;
  } else if (q.includes('samsung') || q.includes('galaxy') || q.includes('s24')) {
    modelName = 'Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)';
    basePrice = 129999;
  } else if (q.includes('boat') || q.includes('airdopes')) {
    modelName = 'boAt Airdopes 141 True Wireless Earbuds';
    basePrice = 1299;
  }

  const amazonPrice = basePrice;
  const flipkartPrice = basePrice - Math.round(basePrice * 0.04);
  const diff = Math.abs(amazonPrice - flipkartPrice);
  const pctDiff = Math.round((diff / amazonPrice) * 1000) / 10;

  return {
    results: [
      {
        product_name: `${modelName}`,
        amazon_price: amazonPrice,
        flipkart_price: flipkartPrice,
        best_platform: "Flipkart",
        difference: diff,
        percentage_difference: pctDiff,
        amazon_product: {
          title: `${modelName} - Official Amazon Listing`,
          price: amazonPrice,
          rating: 4.6,
          url: `https://www.amazon.in/s?k=${encodeURIComponent(modelName)}`,
          image: "https://images-eu.ssl-images-amazon.com/images/I/71v2jvh6nHL._AC_UL320_.jpg",
          platform: "Amazon",
          variants: [{ color: "Black", price: amazonPrice, rating: 4.6, url: `https://www.amazon.in/s?k=${encodeURIComponent(modelName)}`, image: "", title: modelName }]
        },
        flipkart_product: {
          title: `${modelName.toUpperCase()} - Flipkart Store`,
          price: flipkartPrice,
          rating: 4.7,
          url: `https://www.flipkart.com/search?q=${encodeURIComponent(modelName)}`,
          image: "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/h/d/9/-original-imagtc2qznszgzwv.jpeg",
          platform: "Flipkart",
          variants: [{ color: "Black", price: flipkartPrice, rating: 4.7, url: `https://www.flipkart.com/search?q=${encodeURIComponent(modelName)}`, image: "", title: modelName }]
        },
        similarity_score: 98.5
      },
      {
        product_name: `${modelName.replace('128 GB', '256 GB')}`,
        amazon_price: basePrice + 10000,
        flipkart_price: basePrice + 9500,
        best_platform: "Flipkart",
        difference: 500,
        percentage_difference: 0.6,
        amazon_product: {
          title: `${modelName.replace('128 GB', '256 GB')} (Amazon)`,
          price: basePrice + 10000,
          rating: 4.8,
          url: `https://www.amazon.in/s?k=${encodeURIComponent(query)}`,
          image: "https://images-eu.ssl-images-amazon.com/images/I/71v2jvh6nHL._AC_UL320_.jpg",
          platform: "Amazon"
        },
        flipkart_product: {
          title: `${modelName.replace('128 GB', '256 GB').toUpperCase()} (Flipkart)`,
          price: basePrice + 9500,
          rating: 4.7,
          url: `https://www.flipkart.com/search?q=${encodeURIComponent(query)}`,
          image: "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/h/d/9/-original-imagtc2qznszgzwv.jpeg",
          platform: "Flipkart"
        },
        similarity_score: 96.0
      }
    ],
    stats: {
      total_items: 2,
      matched_items: 2,
      amazon_cheaper_count: 0,
      flipkart_cheaper_count: 2,
      equal_count: 0,
      avg_difference_percentage: pctDiff
    },
    source: "demo fallback (backend server offline)"
  };
};

export const searchProducts = async (query) => {
  try {
    const response = await apiClient.post('/api/search', { query });
    return response.data;
  } catch (error) {
    console.warn('Backend API server unreachable or network error, falling back to demo mode:', error);
    // If backend is unreachable (e.g. running on GitHub Pages without local backend server), return realistic demo results
    return generateDemoResults(query);
  }
};

export const getSearchHistory = async () => {
  try {
    const response = await apiClient.get('/api/history');
    return response.data;
  } catch (error) {
    console.warn('Backend API offline, returning sample history:', error);
    return [
      { query: 'iPhone 16 128GB', timestamp: '2026-09-10 18:00:00' },
      { query: 'Samsung Galaxy S24 Ultra', timestamp: '2026-09-10 17:30:00' }
    ];
  }
};

export const clearCache = async () => {
  try {
    const response = await apiClient.post('/api/cache/clear');
    return response.data;
  } catch (error) {
    console.warn('Backend API offline, mock cache cleared:', error);
    return { message: 'Demo cache cleared successfully.' };
  }
};
