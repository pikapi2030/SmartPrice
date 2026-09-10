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
  const q = query.toLowerCase().trim();
  let basePrice = 2499;
  let modelName = query.trim();
  let imageAmazon = "https://images-eu.ssl-images-amazon.com/images/I/61-r9Z4QYqL._AC_UL320_.jpg";
  let imageFlipkart = "https://rukminim2.flixcart.com/image/312/312/xif0q/headphone/e/a/f/-original-imaghn4bhfhgyyhx.jpeg";

  // Category & Brand-based price estimation engine
  if (q.includes('jbl') || q.includes('headphone') || q.includes('earphone') || q.includes('tune') || q.includes('720') || q.includes('520') || q.includes('bt')) {
    modelName = q.includes('720') ? 'JBL Tune 720BT Wireless Headphones (Black)' : 'JBL Wireless Headphones';
    basePrice = 3499;
    imageAmazon = "https://images-eu.ssl-images-amazon.com/images/I/51+Z1+q+o0L._AC_UL320_.jpg";
    imageFlipkart = "https://rukminim2.flixcart.com/image/312/312/xif0q/headphone/e/a/f/-original-imaghn4bhfhgyyhx.jpeg";
  } else if (q.includes('boat') || q.includes('airdopes') || q.includes('earbuds') || q.includes('buds')) {
    modelName = 'boAt Airdopes 141 True Wireless Earbuds';
    basePrice = 1299;
    imageAmazon = "https://images-eu.ssl-images-amazon.com/images/I/61-r9Z4QYqL._AC_UL320_.jpg";
  } else if (q.includes('iphone') || q.includes('apple')) {
    modelName = q.includes('16') ? 'Apple iPhone 16 (128 GB)' : 'Apple iPhone 15 (128 GB)';
    basePrice = 79900;
    imageAmazon = "https://images-eu.ssl-images-amazon.com/images/I/71v2jvh6nHL._AC_UL320_.jpg";
    imageFlipkart = "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/h/d/9/-original-imagtc2qznszgzwv.jpeg";
  } else if (q.includes('samsung') || q.includes('galaxy') || q.includes('s24')) {
    modelName = 'Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)';
    basePrice = 129999;
    imageAmazon = "https://images-eu.ssl-images-amazon.com/images/I/71618r-D-WL._AC_UL320_.jpg";
  } else if (q.includes('laptop') || q.includes('macbook') || q.includes('dell') || q.includes('hp') || q.includes('lenovo')) {
    modelName = `${query.toUpperCase()} Thin & Light Laptop (16GB RAM, 512GB SSD)`;
    basePrice = 49990;
  } else if (q.includes('watch') || q.includes('smartwatch')) {
    modelName = `${query.toUpperCase()} Smartwatch with Heart Rate & SpO2 Monitor`;
    basePrice = 1999;
  } else if (q.includes('redmi') || q.includes('realme') || q.includes('poco') || q.includes('vivo') || q.includes('oppo')) {
    modelName = `${query.toUpperCase()} 5G (8GB RAM, 128GB Storage)`;
    basePrice = 14999;
  } else {
    // Generic product
    basePrice = 2499;
  }

  const amazonPrice = basePrice;
  const flipkartPrice = Math.round(basePrice * 0.94); // ~6% discount on Flipkart
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
          title: `${modelName} - Amazon.in Listing`,
          price: amazonPrice,
          rating: 4.5,
          url: `https://www.amazon.in/s?k=${encodeURIComponent(modelName)}`,
          image: imageAmazon,
          platform: "Amazon",
          variants: [{ color: "Standard", price: amazonPrice, rating: 4.5, url: `https://www.amazon.in/s?k=${encodeURIComponent(modelName)}`, image: "", title: modelName }]
        },
        flipkart_product: {
          title: `${modelName.toUpperCase()} - Flipkart Store`,
          price: flipkartPrice,
          rating: 4.6,
          url: `https://www.flipkart.com/search?q=${encodeURIComponent(modelName)}`,
          image: imageFlipkart,
          platform: "Flipkart",
          variants: [{ color: "Standard", price: flipkartPrice, rating: 4.6, url: `https://www.flipkart.com/search?q=${encodeURIComponent(modelName)}`, image: "", title: modelName }]
        },
        similarity_score: 98.5
      },
      {
        product_name: `${modelName} (Pro/Upgraded Edition)`,
        amazon_price: Math.round(basePrice * 1.25),
        flipkart_price: Math.round(basePrice * 1.22),
        best_platform: "Flipkart",
        difference: Math.round(basePrice * 0.03),
        percentage_difference: 2.4,
        amazon_product: {
          title: `${modelName} (Pro/Upgraded Edition)`,
          price: Math.round(basePrice * 1.25),
          rating: 4.7,
          url: `https://www.amazon.in/s?k=${encodeURIComponent(modelName + ' pro')}`,
          image: imageAmazon,
          platform: "Amazon"
        },
        flipkart_product: {
          title: `${modelName.toUpperCase()} PRO EDITION`,
          price: Math.round(basePrice * 1.22),
          rating: 4.7,
          url: `https://www.flipkart.com/search?q=${encodeURIComponent(modelName + ' pro')}`,
          image: imageFlipkart,
          platform: "Flipkart"
        },
        similarity_score: 95.0
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
