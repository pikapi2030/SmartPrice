import React, { useState, useEffect } from 'react';
import { 
  Search, Sparkles, RefreshCw, ArrowRightLeft, ExternalLink, 
  TrendingDown, Star, History, SlidersHorizontal, AlertTriangle, 
  CheckCircle2, Info, ChevronLeft, ChevronRight, ShoppingBag
} from 'lucide-react';
import { searchProducts, getSearchHistory, clearCache } from './services/api';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState('');
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [source, setSource] = useState('');
  const [history, setHistory] = useState([]);
  const [cacheMessage, setCacheMessage] = useState('');
  
  // Filters & Sorting
  const [sortBy, setSortBy] = useState('price_asc');
  const [matchedOnly, setMatchedOnly] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  // Fetch search history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Cycle loading messages for a rich user experience
  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev + 1) % 4);
      }, 3500);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const fetchHistory = async () => {
    try {
      const data = await getSearchHistory();
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleClearCache = async () => {
    try {
      const data = await clearCache();
      setCacheMessage(data.message);
      setResults([]);
      setStats(null);
      setTimeout(() => setCacheMessage(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to clear cache.');
    }
  };

  const handleSearch = async (e, searchQuery = '') => {
    if (e) e.preventDefault();
    const searchVal = searchQuery || query;
    if (!searchVal.trim()) return;

    setLoading(true);
    setError('');
    setQuery(searchVal);
    setCurrentPage(1);

    try {
      const data = await searchProducts(searchVal);
      setResults(data.results);
      setStats(data.stats);
      setSource(data.source);
      fetchHistory(); // Refresh history pills
    } catch (err) {
      setError(err.message || 'An error occurred during search.');
    } finally {
      setLoading(false);
    }
  };

  const getLoadingMessage = () => {
    switch (loadingStep) {
      case 0:
        return 'Initializing Selenium WebDriver and spoofing headers...';
      case 1:
        return 'Concurrently scraping listings from Amazon India & Flipkart...';
      case 2:
        return 'Parsing HTML layouts and cleansing prices...';
      case 3:
        return 'Aligning matches using RapidFuzz string comparison...';
      default:
        return 'Analyzing prices...';
    }
  };

  // Processing Results (filtering and sorting)
  const filteredResults = results.filter(item => {
    if (matchedOnly) {
      return item.amazon_price !== null && item.flipkart_price !== null;
    }
    return true;
  });

  const sortedResults = [...filteredResults].sort((a, b) => {
    const getCheapest = (item) => {
      if (item.amazon_price !== null && item.flipkart_price !== null) {
        return Math.min(item.amazon_price, item.flipkart_price);
      }
      return item.amazon_price !== null ? item.amazon_price : item.flipkart_price;
    };

    const getRating = (item) => {
      const am = item.amazon_product?.rating || 0;
      const fk = item.flipkart_product?.rating || 0;
      return Math.max(am, fk);
    };

    if (sortBy === 'price_asc') {
      return getCheapest(a) - getCheapest(b);
    }
    if (sortBy === 'price_desc') {
      return getCheapest(b) - getCheapest(a);
    }
    if (sortBy === 'discount_desc') {
      return b.percentage_difference - a.percentage_difference;
    }
    if (sortBy === 'rating_desc') {
      return getRating(b) - getRating(a);
    }
    return 0;
  });

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = sortedResults.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(sortedResults.length / itemsPerPage);

  // Format currency
  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  return (
    <div className="min-h-screen pb-12">
      {/* Background radial glow */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[20%] w-[600px] h-[600px] rounded-full bg-indigo-500/5 blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[20%] w-[600px] h-[600px] rounded-full bg-purple-500/5 blur-[120px]"></div>
      </div>

      {/* Navbar */}
      <header className="sticky top-0 z-10 glass-panel border-b border-slate-900 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-xl shadow-lg shadow-indigo-500/20">
              <ShoppingBag className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                SmartPrice <span className="text-indigo-400 font-medium text-sm px-2 py-0.5 rounded-full bg-indigo-500/10">India</span>
              </h1>
              <p className="text-xs text-slate-400">Real-Time Amazon & Flipkart Price Comparator</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {cacheMessage && (
              <span className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/10 px-3 py-1 rounded-full">
                {cacheMessage}
              </span>
            )}
            <button
              onClick={handleClearCache}
              type="button"
              className="px-3 py-1.5 bg-slate-900 hover:bg-rose-950/25 border border-slate-800 hover:border-rose-900/40 text-slate-300 hover:text-rose-400 rounded-xl transition-all duration-300 flex items-center gap-1.5 text-xs font-medium"
              title="Delete all cached scraped results from database"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Clear Cache</span>
            </button>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>API Server Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 mt-8 relative z-10">
        
        {/* Hero Search Section */}
        <section className="text-center max-w-3xl mx-auto mt-6 mb-12">
          <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4 leading-tight">
            Find the Best Deals <br className="hidden sm:inline" />
            <span className="gradient-text">Across India's Top Stores</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg mb-8 max-w-2xl mx-auto">
            Compare prices instantly between Amazon India and Flipkart. Leveraging real-time Selenium scrapers and RapidFuzz matching to find true comparisons.
          </p>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="relative mb-6">
            <div className="relative flex items-center">
              <Search className="absolute left-4 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search for a product (e.g. iPhone 16, Samsung Galaxy Ultra, Macbook M3)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-12 pr-40 py-4 bg-slate-900/80 hover:bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-2xl text-white outline-none transition-all shadow-xl shadow-black/20 focus:ring-1 focus:ring-indigo-500/50"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="absolute right-2 px-6 py-2.5 gradient-btn rounded-xl flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                <span>Compare</span>
              </button>
            </div>
          </form>

          {/* History Pills */}
          {history.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-2 text-sm mt-3">
              <span className="text-slate-400 flex items-center gap-1">
                <History className="w-3.5 h-3.5" /> Recent Searches:
              </span>
              {history.map((item, idx) => (
                <button
                  key={idx}
                  onClick={(e) => handleSearch(e, item.query)}
                  className="px-3 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-full text-slate-300 hover:text-white transition-all text-xs"
                >
                  {item.query}
                </button>
              ))}
            </div>
          )}
        </section>

        {/* Error Notification */}
        {error && (
          <div className="max-w-3xl mx-auto mb-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-rose-300">Scraping Error</h4>
              <p className="text-xs text-rose-400/90 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Loading Overlay */}
        {loading && (
          <div className="max-w-2xl mx-auto glass-panel p-8 rounded-3xl border border-indigo-500/20 shadow-2xl shadow-indigo-500/10 flex flex-col items-center justify-center text-center my-12 py-16">
            <div className="relative w-16 h-16 mb-6">
              <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
              <div className="absolute inset-0 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin"></div>
              <ArrowRightLeft className="absolute inset-0 m-auto w-6 h-6 text-indigo-400 animate-pulse" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Fetching Prices in Real-Time</h3>
            <p className="text-sm text-slate-400 max-w-md animate-pulse">{getLoadingMessage()}</p>
            
            <div className="mt-8 flex gap-1 w-48 bg-slate-900 p-1 rounded-full overflow-hidden">
              <div className={`h-1.5 rounded-full transition-all duration-700 bg-indigo-500 ${loadingStep >= 0 ? 'w-1/4' : ''}`}></div>
              <div className={`h-1.5 rounded-full transition-all duration-700 bg-indigo-500 ${loadingStep >= 1 ? 'w-1/4' : ''}`}></div>
              <div className={`h-1.5 rounded-full transition-all duration-700 bg-indigo-500 ${loadingStep >= 2 ? 'w-1/4' : ''}`}></div>
              <div className={`h-1.5 rounded-full transition-all duration-700 bg-indigo-500 ${loadingStep >= 3 ? 'w-1/4' : ''}`}></div>
            </div>
          </div>
        )}

        {/* Comparison Dashboard (Stats and Results) */}
        {!loading && results.length > 0 && (
          <div className="space-y-8">
            
            {/* Stats Dashboard */}
            {stats && (
              <div className="glass-panel p-6 rounded-2xl grid grid-cols-2 md:grid-cols-4 gap-6 border-slate-900">
                <div className="text-center md:text-left border-r border-slate-800/50 last:border-none pr-4">
                  <span className="text-xs text-slate-400 uppercase tracking-wider">Matched Listings</span>
                  <div className="text-2xl font-bold mt-1 text-white flex items-center justify-center md:justify-start gap-2">
                    {stats.matched_items}
                    <span className="text-xs px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-md font-normal border border-emerald-500/10">
                      {Math.round((stats.matched_items / stats.total_items) * 100)}% Match
                    </span>
                  </div>
                </div>
                <div className="text-center md:text-left border-r border-slate-800/50 last:border-none pr-4">
                  <span className="text-xs text-slate-400 uppercase tracking-wider">Cheaper on Amazon</span>
                  <div className="text-2xl font-bold mt-1 text-amber-500 flex items-center justify-center md:justify-start gap-1">
                    {stats.amazon_cheaper_count}
                    <span className="text-xs text-slate-400 font-normal">items</span>
                  </div>
                </div>
                <div className="text-center md:text-left border-r border-slate-800/50 last:border-none pr-4">
                  <span className="text-xs text-slate-400 uppercase tracking-wider">Cheaper on Flipkart</span>
                  <div className="text-2xl font-bold mt-1 text-blue-500 flex items-center justify-center md:justify-start gap-1">
                    {stats.flipkart_cheaper_count}
                    <span className="text-xs text-slate-400 font-normal">items</span>
                  </div>
                </div>
                <div className="text-center md:text-left">
                  <span className="text-xs text-slate-400 uppercase tracking-wider">Avg. Price Difference</span>
                  <div className="text-2xl font-bold mt-1 text-indigo-400 flex items-center justify-center md:justify-start gap-1">
                    <TrendingDown className="w-5 h-5" />
                    {stats.avg_difference_percentage}%
                  </div>
                </div>
              </div>
            )}

            {/* Response Source Banner */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800/80">
                <Info className="w-3.5 h-3.5 text-indigo-400" />
                <span>Source: <span className="font-semibold text-slate-200 capitalize">{source} cache</span></span>
              </div>

              {/* Controls */}
              <div className="flex flex-wrap items-center gap-4">
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={matchedOnly}
                    onChange={(e) => {
                      setMatchedOnly(e.target.checked);
                      setCurrentPage(1);
                    }}
                    className="rounded border-slate-800 bg-slate-900 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span>Matches Only</span>
                </label>

                <div className="flex items-center gap-2 text-xs">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-lg text-slate-200 px-2 py-1 focus:outline-none focus:border-indigo-500 text-xs"
                  >
                    <option value="price_asc">Price: Low to High</option>
                    <option value="price_desc">Price: High to Low</option>
                    <option value="discount_desc">Highest Discount</option>
                    <option value="rating_desc">Best Ratings</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {currentItems.map((item, index) => {
                const isMatched = item.amazon_price !== null && item.flipkart_price !== null;
                const best = item.best_platform;
                
                return (
                  <div key={index} className="glass-panel glass-panel-hover rounded-2xl p-5 border-slate-900/60 flex flex-col justify-between relative overflow-hidden">
                    
                    {/* Top match header */}
                    {isMatched && (
                      <div className="absolute top-0 right-0 left-0 bg-slate-900/60 border-b border-slate-800/50 px-4 py-1.5 flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1 font-semibold text-indigo-400">
                          <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Fuzzy Match Confirmed</span>
                        </span>
                        <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-300 rounded font-bold">
                          {item.similarity_score}% score
                        </span>
                      </div>
                    )}

                    {/* Main Content Area */}
                    <div className={`flex gap-4 ${isMatched ? 'mt-7' : ''}`}>
                      
                      {/* Product Thumbnail */}
                      <div className="w-24 h-24 bg-white rounded-xl overflow-hidden flex items-center justify-center p-2 shrink-0 border border-slate-800">
                        <img
                          src={item.amazon_product?.image || item.flipkart_product?.image || "https://images-eu.ssl-images-amazon.com/images/I/61-r9Z4QYqL._AC_UL320_.jpg"}
                          alt={item.product_name}
                          className="max-h-full max-w-full object-contain"
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = "https://images-eu.ssl-images-amazon.com/images/I/61-r9Z4QYqL._AC_UL320_.jpg";
                          }}
                        />
                      </div>

                      {/* Product details */}
                      <div className="space-y-1 min-w-0">
                        <h3 className="text-sm font-semibold text-slate-100 line-clamp-2 leading-snug hover:text-indigo-400 transition-colors" title={item.product_name}>
                          {item.product_name}
                        </h3>
                        
                        {/* Highlights */}
                        {isMatched && best !== 'Equal' && (
                          <div className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full mt-1 border border-emerald-500/10">
                            <TrendingDown className="w-3 h-3" />
                            Cheaper on {best} by {formatCurrency(item.difference)} ({item.percentage_difference}%)
                          </div>
                        )}
                        {isMatched && best === 'Equal' && (
                          <div className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-400 bg-slate-500/10 px-2 py-0.5 rounded-full mt-1">
                            Prices are equal on both platforms
                          </div>
                        )}
                        {!isMatched && (
                          <div className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full mt-1 border border-amber-500/10">
                            Unique listing on {best}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Platforms Comparison Blocks */}
                    <div className="grid grid-cols-2 gap-4 mt-5 pt-4 border-t border-slate-800/50">
                      
                      {/* Amazon Block */}
                      <div className={`p-3 rounded-xl border flex flex-col justify-between ${
                        item.amazon_price !== null 
                          ? (isMatched && best === 'Amazon' ? 'bg-amber-500/5 border-amber-500/30 ring-1 ring-amber-500/20' : 'bg-slate-900/50 border-slate-800')
                          : 'bg-slate-950/20 border-dashed border-slate-900 opacity-40'
                      }`}>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[10px] font-bold text-amber-500 uppercase tracking-wide">Amazon.in</span>
                          {isMatched && best === 'Amazon' && (
                            <span className="text-[9px] px-1.5 py-0.2 bg-amber-500 text-slate-950 font-bold rounded">CHEAPEST</span>
                          )}
                        </div>
                        
                        {item.amazon_price !== null ? (
                          <div>
                            <div className="text-base font-extrabold text-white">
                              {formatCurrency(item.amazon_price)}
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              <span className="text-xs text-slate-400 flex items-center gap-0.5">
                                <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                                {item.amazon_product?.rating || 'N/A'}
                              </span>
                            </div>
                            {item.amazon_product?.variants && item.amazon_product.variants.length > 1 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {item.amazon_product.variants.map((v, vIdx) => (
                                  <span 
                                    key={vIdx} 
                                    className="text-[9px] px-1.5 py-0.5 bg-slate-800/80 text-slate-300 rounded border border-slate-700/50 leading-none"
                                    title={`Price: ${formatCurrency(v.price)}`}
                                  >
                                    {v.color}
                                  </span>
                                ))}
                              </div>
                            )}
                            <a 
                              href={item.amazon_product?.url} 
                              target="_blank" 
                              rel="noreferrer" 
                              className="mt-3 text-[11px] font-semibold text-amber-400 hover:text-amber-300 flex items-center gap-1 group w-fit"
                            >
                              <span>Visit Store</span>
                              <ExternalLink className="w-3 h-3 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                            </a>
                          </div>
                        ) : (
                          <div className="text-xs text-slate-500 py-4 italic">Not Available</div>
                        )}
                      </div>

                      {/* Flipkart Block */}
                      <div className={`p-3 rounded-xl border flex flex-col justify-between ${
                        item.flipkart_price !== null 
                          ? (isMatched && best === 'Flipkart' ? 'bg-blue-500/5 border-blue-500/30 ring-1 ring-blue-500/20' : 'bg-slate-900/50 border-slate-800')
                          : 'bg-slate-950/20 border-dashed border-slate-900 opacity-40'
                      }`}>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wide">Flipkart</span>
                          {isMatched && best === 'Flipkart' && (
                            <span className="text-[9px] px-1.5 py-0.2 bg-blue-500 text-white font-bold rounded">CHEAPEST</span>
                          )}
                        </div>
                        
                        {item.flipkart_price !== null ? (
                          <div>
                            <div className="text-base font-extrabold text-white">
                              {formatCurrency(item.flipkart_price)}
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              <span className="text-xs text-slate-400 flex items-center gap-0.5">
                                <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                                {item.flipkart_product?.rating || 'N/A'}
                              </span>
                            </div>
                            {item.flipkart_product?.variants && item.flipkart_product.variants.length > 1 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {item.flipkart_product.variants.map((v, vIdx) => (
                                  <span 
                                    key={vIdx} 
                                    className="text-[9px] px-1.5 py-0.5 bg-slate-800/80 text-slate-300 rounded border border-slate-700/50 leading-none"
                                    title={`Price: ${formatCurrency(v.price)}`}
                                  >
                                    {v.color}
                                  </span>
                                ))}
                              </div>
                            )}
                            <a 
                              href={item.flipkart_product?.url} 
                              target="_blank" 
                              rel="noreferrer" 
                              className="mt-3 text-[11px] font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1 group w-fit"
                            >
                              <span>Visit Store</span>
                              <ExternalLink className="w-3 h-3 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                            </a>
                          </div>
                        ) : (
                          <div className="text-xs text-slate-500 py-4 italic">Not Available</div>
                        )}
                      </div>

                    </div>

                  </div>
                );
              })}
            </div>

            {/* Empty state for filter match */}
            {sortedResults.length === 0 && (
              <div className="text-center py-16 glass-panel rounded-3xl border-slate-900">
                <AlertTriangle className="w-10 h-10 text-slate-400 mx-auto mb-3 animate-bounce" />
                <p className="text-slate-300 font-semibold">No results match your criteria.</p>
                <p className="text-slate-500 text-xs mt-1">Try disabling "Matches Only" or adjust sorting filters.</p>
              </div>
            )}

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-4 mt-8 pt-4">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-sm text-slate-400">
                  Page <span className="text-white font-semibold">{currentPage}</span> of <span className="text-slate-300">{totalPages}</span>
                </span>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}

          </div>
        )}

        {/* Brand Showcase if no search has been run */}
        {!loading && results.length === 0 && (
          <section className="max-w-4xl mx-auto mt-8 p-8 glass-panel rounded-3xl border-slate-900">
            <div className="flex items-center gap-2 mb-4 text-xs font-semibold uppercase tracking-wider text-indigo-400">
              <Sparkles className="w-3.5 h-3.5" /> Getting Started
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Try searching for products like:</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
              <button 
                onClick={(e) => handleSearch(e, "iPhone 16 128GB")}
                className="p-4 bg-slate-900/60 hover:bg-slate-900 border border-slate-850 hover:border-slate-800 text-left rounded-2xl group transition-all"
              >
                <div className="font-semibold text-sm text-white group-hover:text-indigo-400 transition-colors">iPhone 16 128GB</div>
                <div className="text-xs text-slate-500 mt-1">Compare colors and models from Apple stores</div>
              </button>
              <button 
                onClick={(e) => handleSearch(e, "Samsung Galaxy S24 Ultra")}
                className="p-4 bg-slate-900/60 hover:bg-slate-900 border border-slate-850 hover:border-slate-800 text-left rounded-2xl group transition-all"
              >
                <div className="font-semibold text-sm text-white group-hover:text-indigo-400 transition-colors">Samsung Galaxy S24 Ultra</div>
                <div className="text-xs text-slate-500 mt-1">Compare high-end titanium phones</div>
              </button>
              <button 
                onClick={(e) => handleSearch(e, "boAt Airdopes")}
                className="p-4 bg-slate-900/60 hover:bg-slate-900 border border-slate-850 hover:border-slate-800 text-left rounded-2xl group transition-all"
              >
                <div className="font-semibold text-sm text-white group-hover:text-indigo-400 transition-colors">boAt Airdopes</div>
                <div className="text-xs text-slate-500 mt-1">Compare budget true wireless earphones</div>
              </button>
            </div>
          </section>
        )}

      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 mt-20 border-t border-slate-900 pt-6 text-center text-xs text-slate-500">
        <p className="mt-1">Disclaimer: All product names, logos, and brands are property of their respective owners. Prices are scraped in real-time or cached from public web pages.</p>
      </footer>
    </div>
  );
}

export default App;
