import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { queryAI, updateProfile, placeOrder, getOrders, bulkPlaceOrder, cancelOrder, getCart, addToCart as addToCartAPI, updateCart, removeFromCart, clearCart, getWishlist, toggleWishlist as toggleWishlistAPI } from '../api';
import { Search, MessageSquare, User, LogOut, Package, CheckCircle, Send, ShoppingCart, CreditCard, X, ArrowLeft, Heart, Plus, Minus } from 'lucide-react';
import './Home.css';

const BACKEND_URL = 'http://localhost:8000';

const agentData = {
    recommendation: {
        title: "Recommendation Agent",
        lines: ["Understands user preferences.", "Suggests suitable outfits.", "Learns from interactions."]
    },
    pricing: {
        title: "Pricing Agent",
        lines: ["Filters by budget.", "Best value approach.", "Applies limits strictly."]
    },
    inventory: {
        title: "Inventory Agent",
        lines: ["Checks availability.", "Ensures stock exists.", "Size verification."]
    },
    chat: {
        title: "Chat Agent",
        lines: ["Natural language queries.", "Action mapping.", "Shopping guides."]
    }
};

const Home = () => {
    const [prompt, setPrompt] = useState('');
    const [products, setProducts] = useState([]);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [aiMessage, setAiMessage] = useState('');
    const [showAddressModal, setShowAddressModal] = useState(false);
    const [addressLabel, setAddressLabel] = useState('Home');
    const [addressText, setAddressText] = useState('');
    const [orderStatus, setOrderStatus] = useState(null);
    const [showChatPopup, setShowChatPopup] = useState(false);
    const [hasInteracted, setHasInteracted] = useState(false);

    // No-Click Navigation States
    const [currentView, setCurrentView] = useState('home'); // home, detail, checkout, success
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [selectedAddress, setSelectedAddress] = useState('');
    const [paymentMethod, setPaymentMethod] = useState('COD');
    const [showAgentInfo, setShowAgentInfo] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [historyStack, setHistoryStack] = useState(['home']);
    const [wishlist, setWishlist] = useState([]);
    const [cartList, setCartList] = useState([]);
    const [ordersList, setOrdersList] = useState([]);
    const [detailQty, setDetailQty] = useState(1);
    const [detailSize, setDetailSize] = useState('M');
    const [isBulkCheckout, setIsBulkCheckout] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(storedUser);
            // Normalize address to object if it's a string
            let addrObj = parsedUser.address;
            if (typeof addrObj === 'string' && addrObj) {
                try {
                    addrObj = JSON.parse(addrObj);
                } catch {
                    addrObj = { "Default": addrObj };
                }
            } else if (!addrObj) {
                addrObj = {};
            }
            parsedUser.address = addrObj;
            setUser(parsedUser);
            if (Object.keys(addrObj).length > 0) {
                setSelectedAddress(Object.values(addrObj)[0]);
            }
            // Fetch all user data from database
            fetchOrders(parsedUser.id);
            fetchCartData(parsedUser.id);
            fetchWishlistData(parsedUser.id);
        }
    }, [navigate]);

    const fetchOrders = async (userId) => {
        try {
            const res = await getOrders(userId);
            setOrdersList(res.data);
        } catch (err) {
            console.error("Fetch Orders Error:", err);
        }
    };

    const fetchCartData = async (userId) => {
        try {
            const res = await getCart(userId);
            setCartList(res.data);
        } catch (err) {
            console.error("Fetch Cart Error:", err);
        }
    };

    const fetchWishlistData = async (userId) => {
        try {
            const res = await getWishlist(userId);
            // Transform wishlist data to match expected format
            // item.product is the Foreign Key ID from the serializer
            const wishlistProducts = res.data.map(item => ({
                product_id: item.product,
                wishlist_id: item.wishlist_id,
                product_name: item.product_name,
                product_image: item.product_image,
                price: item.product_price,
                product_category: item.product_category,
                product_description: item.product_description,
                color: item.color,
                stock: item.stock
            }));
            setWishlist(wishlistProducts);
        } catch (err) {
            console.error("Fetch Wishlist Error:", err);
        }
    };

    // Navigation Helpers
    const navigateToView = (viewName) => {
        if (currentView === viewName) return;
        setHistoryStack(prev => [...prev, viewName]);
        setCurrentView(viewName);
    };

    const handleBackView = () => {
        if (historyStack.length > 1) {
            const newStack = [...historyStack];
            newStack.pop(); // Remove current view
            const previousView = newStack[newStack.length - 1];
            setHistoryStack(newStack);
            setCurrentView(previousView);
        }
    };

    const toggleWishlist = async (product) => {
        if (!user) return;

        // Optimistic Update with Robust ID Coercion
        const productIdStr = String(product.product_id);
        const isCurrentlyInWishlist = wishlist.some(p => String(p.product_id || p) === productIdStr);
        let newWishlist;

        if (isCurrentlyInWishlist) {
            newWishlist = wishlist.filter(p => String(p.product_id || p) !== productIdStr);
        } else {
            newWishlist = [...wishlist, product];
        }
        setWishlist(newWishlist);

        try {
            await toggleWishlistAPI({
                user_id: user.id,
                product_id: product.product_id
            });
            // Background sync
            fetchWishlistData(user.id);
        } catch (err) {
            console.error("Toggle Wishlist Error:", err);
            // Revert on error
            fetchWishlistData(user.id);
        }
    };

    const addToCart = async (prod, qty, size) => {
        if (!user) return;
        try {
            await addToCartAPI({
                user_id: user.id,
                product_id: prod.product_id,
                quantity: qty,
                size: size
            });
            setAiMessage(`Added ${qty}x ${prod.product_name} (${size}) to your cart.`);
            // Refresh cart from database
            fetchCartData(user.id);
        } catch (err) {
            console.error("Add to Cart Error:", err);
        }
    };

    const handleProductClick = (product) => {
        // Navigate to product detail view when clicking on product card
        setSelectedProduct(product);
        setDetailQty(1);
        setDetailSize('M');
        setIsBulkCheckout(false);
        navigateToView('detail');
    };

    const handleRemoveFromCart = async (cartId) => {
        if (!user) return;

        // Optimistic UI Update
        const newCartList = cartList.filter(item => item.cart_id !== cartId);
        setCartList(newCartList);

        try {
            await removeFromCart({ cart_id: cartId });
            // Refresh from DB to be sure
            fetchCartData(user.id);
        } catch (err) {
            console.error("Remove from Cart Error:", err);
            // Revert on error
            fetchCartData(user.id);
        }
    };

    const handleUpdateCartQty = async (item, change) => {
        if (!user) return;
        const newQty = item.quantity + change;

        if (newQty < 1) {
            // Confirm removal if quantity goes to 0 (optional user exp choice, for now just remove)
            handleRemoveFromCart(item.cart_id);
            return;
        }

        // Optimistic Update
        const newCartList = cartList.map(cItem =>
            cItem.cart_id === item.cart_id ? { ...cItem, quantity: newQty } : cItem
        );
        setCartList(newCartList);

        try {
            await updateCart({
                cart_id: item.cart_id,
                quantity: newQty
            });
            // We verify with DB later, but optimistic update keeps UI snappy
        } catch (err) {
            console.error("Update Cart Quantity Error:", err);
            fetchCartData(user.id); // Revert
        }
    };

    const handleAutonomousAction = async (json, productsList = []) => {
        const { intent, action, product_reference, payment_method, shipping_address_label, manual_full_address, quantity, address_action } = json;

        // Dynamic Index Resolution
        const resolveProductIndex = (ref) => {
            if (!ref) return -1;
            const lowerRef = ref.toLowerCase();
            const ordinals = {
                'first': 0, '1st': 0,
                'second': 1, '2nd': 1,
                'third': 2, '3rd': 2,
                'fourth': 3, '4th': 3,
                'fifth': 4, '5th': 4,
                'sixth': 5, '6th': 5,
                'seventh': 6, '7th': 6,
                'eighth': 7, '8th': 7,
                'ninth': 8, '9th': 8,
                'tenth': 9, '10th': 9
            };
            if (ordinals[lowerRef] !== undefined) return ordinals[lowerRef];
            if (lowerRef === 'last') return productsList.length - 1;
            const numMatch = lowerRef.match(/\d+/);
            if (numMatch) return parseInt(numMatch[0]) - 1;
            return -1;
        };

        // 0. ADDRESS ACTION
        if (address_action === 'open') {
            setShowAddressModal(true);
        }

        // 1. PRODUCT RESOLUTION (Strict Isolation)
        let product = null;
        const ref = product_reference?.toLowerCase();

        // High Priority: Explicit Reference (this, it, that) or Index (1st, 2nd)
        if (ref) {
            if (['this', 'that', 'it'].includes(ref) && selectedProduct) {
                product = selectedProduct;
            } else {
                const idx = resolveProductIndex(ref);
                if (idx >= 0 && idx < productsList.length) {
                    product = productsList[idx];
                }
            }
        }

        // Mid Priority: If search results were returned specifically for this query, use the top result
        // This is crucial for "Buy blue shirt" while viewing a red one.
        if (!product && productsList.length > 0) {
            product = productsList[0];
        }

        // Low Priority: Fallback to selectedProduct only if it's the current context and no search results were generated
        if (!product && selectedProduct && currentView === 'detail') {
            product = selectedProduct;
        }

        // 2. ORDER INTENT HANDLING
        if (intent === 'order') {
            // 2.1 CONTEXT: CART PAGE (Intent Capture -> Navigate)
            if (currentView === 'cart') {
                // PRIORITIZE: Manual Exact String > Label Lookup
                let targetAddress = manual_full_address; // e.g. "2-45, KPHB, Hyderabad" given in prompt

                if (!targetAddress && shipping_address_label) {
                    const userAddresses = user.address || {};
                    const key = Object.keys(userAddresses).find(k => k.toLowerCase() === shipping_address_label.toLowerCase());
                    if (key) targetAddress = userAddresses[key];
                }

                // If still no address, try to fall back to 'selectedAddress' if it was already set? 
                // No, the prompt "Order to X" is explicit. If X isn't found, we should warn or ask?
                // But rules say: "Treat any user-typed address as a valid temporary delivery address." -> `manual_full_address` covers this.

                if (targetAddress) {
                    setSelectedAddress(targetAddress);
                }
                if (payment_method) setPaymentMethod(payment_method);

                setAiMessage("Proceeding to checkout with your specified details.");
                handleBulkCheckout();
                return;
            }

            // 2.2 CONTEXT: CHECKOUT PAGE (Execution)
            if (currentView === 'checkout') {
                // Allow last-minute updates
                let targetAddress = manual_full_address;
                if (!targetAddress && shipping_address_label) {
                    const userAddresses = user.address || {};
                    const key = Object.keys(userAddresses).find(k => k.toLowerCase() === shipping_address_label.toLowerCase());
                    if (key) targetAddress = userAddresses[key];
                }

                const finalAddress = targetAddress || selectedAddress;
                const finalPayment = payment_method || paymentMethod;

                if (targetAddress) setSelectedAddress(targetAddress);
                if (payment_method) setPaymentMethod(payment_method);

                if (!finalAddress) {
                    setAiMessage("Please select a delivery address to confirm the order.");
                    return;
                }

                setAiMessage("Confirming your order...");

                if (isBulkCheckout) {
                    // Bulk Order
                    // We need to call confirmBulkOrder but it uses state, so ensuring state is set might be race-y if we call immediately
                    // But setState is async. 
                    // However, selectedAddress and paymentMethod are state. 
                    // PRO TIP: pass args to functions or rely on user confirming? 
                    // The prompt says "Prompt actions ... must always give the same result".
                    // "Never place an order without final confirmation on Checkout page" -> Wait, 
                    // "Accept prompts such as 'Confirm order' ... Checkout steps: 1. Confirm..."
                    // "After address and payment are confirmed on the Checkout page: Place the order successfully."

                    // Since I cannot guarantee state update finishes before this call if I call it now,
                    // I will trust the existing state OR the extracted values if I could pass them.
                    // confirmBulkOrder uses `selectedAddress` and `paymentMethod` from state.
                    // If I just set them, they won't be ready.
                    // Ideally, I should strictly rely on what is ON SCREEN.
                    // If the user says "Pay via UPI", I update state. The user sees it. 
                    // If the user says "Confirm order", I execute.
                    // If the user says "Order with UPI", I should update AND execute?
                    // React state updates are batched/async. 

                    // FOR ROBUSTNESS: If new info is provided, just update and ask to confirm?
                    // "Never place an order without final confirmation on Checkout page"
                    // Doing update + confirm in one shot is risky with React State.

                    // Simple approach: If prompt effectively is "Confirm", execute.
                    // If prompt changes data ("pay via card"), just change data.

                    if (payment_method || shipping_address_label || manual_full_address) {
                        setAiMessage("Updated order details. Say 'Confirm' to place the order.");
                        return; // Stop here, let user confirm new details
                    }

                    confirmBulkOrder();
                } else if (selectedProduct) {
                    // Single Product
                    if (payment_method || shipping_address_label || manual_full_address) {
                        setAiMessage("Updated order details. Say 'Confirm' to place the order.");
                        return;
                    }

                    handlePlaceOrder(selectedProduct.product_id, finalPayment, finalAddress, detailQty, (currentView === 'detail' ? detailSize : (selectedProduct.size || 'M')));
                }
                return;
            }

            // 2.3 CANCELLATION
            if (action === 'cancel') {
                const { order_id: targetId } = json;
                if (targetId) {
                    setAiMessage(`Attempting to cancel order #${targetId}...`);
                    handleCancelOrder(targetId);
                    return;
                } else {
                    setAiMessage("Please provide the order ID you'd like to cancel (e.g., 'Cancel order 12').");
                    navigateToView('orders');
                    return;
                }
            }

            // 2.4 DIRECT ORDER DETECTION (Home/Detail/Search Context)
            if (product) {
                let targetAddress = manual_full_address;
                if (!targetAddress && shipping_address_label) {
                    const userAddresses = user.address || {};
                    targetAddress = userAddresses[shipping_address_label] || userAddresses[Object.keys(userAddresses).find(k => k.toLowerCase() === shipping_address_label.toLowerCase())];
                }

                // Fallback: If intent is order but no address found, try the first saved one
                if (!targetAddress && user.address && typeof user.address === 'object' && Object.keys(user.address).length > 0) {
                    const labels = Object.keys(user.address);
                    targetAddress = user.address[labels[0]];
                }

                if (targetAddress) {
                    // If AI didn't return a qty, use detail page qty if we are in detail view
                    const qty = quantity || (currentView === 'detail' ? detailQty : 1);
                    const orderSize = (currentView === 'detail' ? detailSize : (product.size || 'M'));

                    setAiMessage(`Directly ordering ${qty}x "${product.product_name}" to ${targetAddress}...`);
                    handlePlaceOrder(product.product_id, payment_method || 'COD', targetAddress, qty, orderSize);
                    return;
                } else if (shipping_address_label || manual_full_address) {
                    setAiMessage(`I identified a delivery request but couldn't finalize the address. Please select or enter one.`);
                    setSelectedProduct(product);
                    navigateToView('checkout');
                    return;
                } else {
                    // General "Checkout this" without address
                    setSelectedProduct(product);
                    setIsBulkCheckout(false);
                    navigateToView('checkout');
                    if (payment_method) setPaymentMethod(payment_method);
                    return;
                }
            } else if (action === 'checkout') {
                // General "Checkout" command without specific product -> implies Bulk/Cart if not empty, or just error
                if (cartList.length > 0) {
                    handleBulkCheckout();
                } else {
                    setAiMessage("Your cart is empty and no product selected.");
                }
                return;
            }
        }

        if (intent === 'payment' && action === 'complete') {
            if (currentView === 'checkout' && selectedProduct) {
                handlePlaceOrder(selectedProduct.product_id, paymentMethod || 'COD', selectedAddress);
            } else {
                setAiMessage("We are not at the payment stage yet.");
            }
        }

        if (intent === 'search' && (action === 'list' || action === 'back')) {
            if (action === 'back' || (intent === 'search' && action === 'back')) {
                handleBackView();
            } else {
                navigateToView('home');
            }
        }

        if (intent === 'cart') {
            if (action === 'add') {
                // If specific product identified
                if (product) {
                    setAiMessage(`Adding "${product.product_name}" to your cart...`);
                    addToCart(product, quantity || 1, product.size || 'M');
                } else {
                    setAiMessage("Which item should I add to your cart?");
                }
            } else {
                navigateToView('cart');
            }
        }

        if (intent === 'wishlist') {
            if (action === 'add') {
                if (product) {
                    // Check if already in wishlist to avoid toggle-remove
                    const productIdStr = String(product.product_id);
                    const isIn = wishlist.some(p => String(p.product_id || p) === productIdStr);

                    if (!isIn) {
                        setAiMessage(`Adding "${product.product_name}" to your wishlist...`);
                        toggleWishlist(product);
                    } else {
                        setAiMessage(`"${product.product_name}" is already in your wishlist.`);
                    }
                } else {
                    setAiMessage("Which item should I add to the wishlist?");
                }
            } else {
                navigateToView('wishlist');
            }
        }

        if (intent === 'order' && action === 'list') {
            fetchOrders(user.id);
            navigateToView('orders');
        }
    };

    const handleSearch = async (e, customPrompt = null) => {
        if (e) e.preventDefault();
        const searchPrompt = customPrompt || prompt;
        if (!searchPrompt && !customPrompt) return;

        const lowerPrompt = searchPrompt.toLowerCase();
        if (['home', 'go home', 'back', 'back to home', 'main page'].includes(lowerPrompt)) {
            if (lowerPrompt.includes('back')) {
                handleBackView();
            } else {
                setProducts([]);
                setHasInteracted(false);
                navigateToView('home');
                setAiMessage("");
                setSelectedProduct(null);
            }
            setPrompt('');
            return;
        }

        if (lowerPrompt.includes('open wishlist') || lowerPrompt.includes('show wishlist')) {
            navigateToView('wishlist');
            setPrompt('');
            return;
        }
        if (lowerPrompt.includes('open cart') || lowerPrompt.includes('show cart')) {
            navigateToView('cart');
            setPrompt('');
            return;
        }
        if (lowerPrompt.includes('open orders') || lowerPrompt.includes('show orders') || lowerPrompt.includes('order history')) {
            fetchOrders(user.id);
            navigateToView('orders');
            setPrompt('');
            return;
        }

        setHasInteracted(true);
        setLoading(true);
        setPrompt('');

        try {
            const response = await queryAI({ prompt: searchPrompt, user_id: user.id });

            if (response.data) {
                const { machine_readable_json, message, products: newProducts } = response.data;
                setAiMessage(message || "Analyzing request...");

                const isNewSearch = machine_readable_json?.intent === 'search' || (newProducts && newProducts.length > 0);
                let activeProducts = products;

                if (isNewSearch && Array.isArray(newProducts)) {
                    setProducts(newProducts);
                    activeProducts = newProducts;
                }

                if (machine_readable_json) {
                    handleAutonomousAction(machine_readable_json, activeProducts);
                }
            }
        } catch (err) {
            console.error("AI Search Error:", err);
            setAiMessage("AI Agents are offline. Please try again later.");
        } finally {
            setLoading(false);
            setShowChatPopup(false);
        }
    };

    const handleBulkCheckout = async () => {
        if (!cartList.length) return;
        setIsBulkCheckout(true);
        setSelectedProduct(null); // Ensure no single product is selected
        navigateToView('checkout');

        if (!selectedAddress && Object.keys(user.address || {}).length > 0) {
            setSelectedAddress(Object.values(user.address)[0]);
        }
    };

    // Actually place the bulk order
    const confirmBulkOrder = async () => {
        if (!cartList.length) return;
        if (!selectedAddress) {
            setAiMessage("Please select a delivery address.");
            setShowAddressModal(true);
            return;
        }

        setLoading(true);
        try {
            const response = await bulkPlaceOrder({
                user_id: user.id,
                items: cartList,
                payment_method: paymentMethod,
                delivery_address: selectedAddress
            });

            setOrderStatus({
                bulk: true,
                message: "Bulk Order Placed Successfully",
                ...response.data.bulk_details
            });

            // Clear cart from database
            await clearCart({ user_id: user.id });
            // Refresh cart from database
            fetchCartData(user.id);
            fetchOrders(user.id);
            navigateToView('success');
            setAiMessage("Your cart order has been placed successfully!");
        } catch (err) {
            console.error("Bulk Order Error:", err);
            setAiMessage(err.response?.data?.error || "Failed to place bulk order. Please try again.");
            if (err.response?.data?.error?.toLowerCase().includes("address")) {
                setShowAddressModal(true);
            }
        } finally {
            setLoading(false);
        }
    };

    const handlePlaceOrder = async (productId, pMethod, pAddress, pQty = 1, pSize = 'M') => {
        setLoading(true);
        try {
            const response = await placeOrder({
                user_id: user.id,
                product_id: productId,
                payment_method: pMethod,
                delivery_address: pAddress,
                quantity: pQty,
                size: pSize
            });
            setOrderStatus(response.data.order_details);
            fetchOrders(user.id); // Refresh orders list
            navigateToView('success');
            setAiMessage(`Order #${response.data.order_details.order_id} placed successfully!`);
        } catch (err) {
            setAiMessage(err.response?.data?.error || "Order failed");
            if (err.response?.data?.error?.toLowerCase().includes("address")) {
                setShowAddressModal(true);
            }
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const handleCancelOrder = async (orderId) => {
        setLoading(true);
        try {
            await cancelOrder({ order_id: orderId });
            setAiMessage(`Order #${orderId} cancelled successfully.`);
            fetchOrders(user.id); // Refresh
        } catch (err) {
            console.error("Cancellation failed:", err);
            // Silent error as requested, but log for debugging
        } finally {
            setLoading(false);
        }
    };

    const saveAddress = () => {
        const newAddresses = { ...user.address, [addressLabel]: addressText };
        updateProfile(user.id, { address: newAddresses }).then(r => {
            const updatedUser = { ...r.data.user, address: newAddresses };
            setUser(updatedUser);
            localStorage.setItem('user', JSON.stringify(updatedUser));
            setShowAddressModal(false);
            setSelectedAddress(addressText);
        });
    };

    if (!user) return null;

    return (
        <div className="home-container autonomous">
            <aside className="sidebar">
                <div className="sidebar-brand"><h1>Fashiopulse AI</h1></div>
                <nav className="sidebar-nav">
                    <div className="section-title">AI Agents</div>
                    {Object.entries(agentData).map(([id, data]) => (
                        <div key={id} className="agent-item active clickable" onClick={() => { setSelectedAgent(data); setShowAgentInfo(true); }}>
                            <CheckCircle size={16} /> <span>{data.title}</span>
                        </div>
                    ))}

                    <div className="section-title" style={{ marginTop: '30px' }}>Personal Space</div>
                    <div className={`agent-item clickable ${currentView === 'wishlist' ? 'active' : ''}`} onClick={() => navigateToView('wishlist')}>
                        <Heart size={16} /> <span>Wishlist</span>
                    </div>
                    <div className={`agent-item clickable ${currentView === 'cart' ? 'active' : ''}`} onClick={() => navigateToView('cart')}>
                        <ShoppingCart size={16} /> <span>Cart</span>
                    </div>
                    <div className={`agent-item clickable ${currentView === 'orders' ? 'active' : ''}`} onClick={() => navigateToView('orders')}>
                        <Package size={16} /> <span>My Orders</span>
                    </div>
                </nav>
                <div className="sidebar-footer">
                    <div className="user-profile-simple" onClick={() => setShowAddressModal(true)}>
                        <User size={20} />
                        <div className="p-info"><strong>{user.name}</strong><p>{user.email}</p></div>
                    </div>
                    <button className="logout-link" onClick={logout}><LogOut size={16} /> Logout</button>
                </div>
            </aside>

            <main className="main-content">
                <header className="autonomous-header">
                    <div className="prompt-container">
                        <form onSubmit={handleSearch}>
                            <input type="text" placeholder="Order anything by name, number, or to a specific address..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
                            <button type="submit" className="ask-submit">Ask AI</button>
                        </form>
                    </div>
                </header>

                {historyStack.length > 1 && (
                    <div className="back-nav-lane">
                        <button className="global-back-btn fade-in" onClick={handleBackView}>
                            <ArrowLeft size={18} style={{ marginRight: '5px' }} /> <span>Back</span>
                        </button>
                    </div>
                )}

                <section className="experience-area">
                    {loading && <div className="autonomous-loader"><span>Processing...</span></div>}

                    {currentView === 'home' && (
                        <div className="view-container slide-up">
                            <div className="welcome-section">
                                <h2>Welcome, <strong>{user.name}</strong>!</h2>
                                {!hasInteracted ? <p className="helper-text">I can find, open, and order products for you. Try "Order the 2nd one to my Home address".</p> : (!products.length && !loading && <p className="hint">No products found.</p>)}
                            </div>
                            <div className="auto-grid">
                                {products.map((p, i) => (
                                    <div key={p.product_id} className="auto-card" onClick={() => handleProductClick(p)}>
                                        <div className="card-num">{i + 1}</div>
                                        <div className="card-img-wrapper"><img src={p.product_image ? `${BACKEND_URL}${p.product_image}` : 'https://placehold.co/400x500?text=N/A'} alt={p.product_name} /></div>
                                        <div className="card-details"><h3>{p.product_name}</h3><div className="price-row"><span>₹{p.price}</span> <span className="s-tag">{p.size}</span></div></div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {currentView === 'detail' && selectedProduct && (
                        <div className="view-container detail-view fade-in">
                            <div className="detail-layout">
                                <div className="detail-img-wrapper">
                                    <img src={selectedProduct.product_image ? `${BACKEND_URL}${selectedProduct.product_image}` : 'https://placehold.co/600x800?text=N/A'} alt={selectedProduct.product_name} />
                                    <button className={`wishlist-btn ${(wishlist.some(p => String(p.product_id || p) === String(selectedProduct.product_id))) ? 'active' : ''}`} onClick={() => toggleWishlist(selectedProduct)}>
                                        <Heart fill={(wishlist.some(p => String(p.product_id || p) === String(selectedProduct.product_id))) ? '#ff4d4d' : 'transparent'} color={(wishlist.some(p => String(p.product_id || p) === String(selectedProduct.product_id))) ? '#ff4d4d' : '#fff'} size={24} />
                                    </button>
                                </div>
                                <div className="detail-content">
                                    <div className="detail-header">
                                        <span className="cat-tag">{selectedProduct.product_category}</span>
                                        <h1>{selectedProduct.product_name}</h1>
                                        <p className="price-tag">₹{selectedProduct.price}</p>
                                    </div>

                                    <div className="detail-section">
                                        <label>Select Size</label>
                                        <div className="size-selector">
                                            {['XS', 'S', 'M', 'L', 'XL', 'XXL'].map(sz => (
                                                <button key={sz} className={`size-btn ${detailSize === sz ? 'active' : ''}`} onClick={() => setDetailSize(sz)}>{sz}</button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="detail-section">
                                        <label>Quantity</label>
                                        <div className="qty-picker">
                                            <button onClick={() => setDetailQty(Math.max(1, detailQty - 1))}><Minus size={18} /></button>
                                            <span className="qty-val">{detailQty}</span>
                                            <button onClick={() => setDetailQty(detailQty + 1)}><Plus size={18} /></button>
                                        </div>
                                    </div>

                                    <div className="auto-actions">
                                        <button className="sec-btn" onClick={() => addToCart(selectedProduct, detailQty, detailSize)}>Add to Cart</button>
                                        <button className="prime-btn" onClick={() => {
                                            setIsBulkCheckout(false);
                                            navigateToView('checkout');
                                            if (!selectedAddress && Object.keys(user.address).length > 0) setSelectedAddress(Object.values(user.address)[0]);
                                        }}>Buy Now</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {currentView === 'checkout' && (selectedProduct || isBulkCheckout) && (
                        <div className="view-container checkout-view fade-in">
                            <h2>{isBulkCheckout ? 'Checkout (Bulk)' : 'Checkout'}</h2>
                            <div className="checkout-card">
                                {isBulkCheckout ? (
                                    <div className="checkout-bulk-preview">
                                        <h3>Review {cartList.length} Items</h3>
                                        <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #eee', padding: '10px', borderRadius: '8px', marginBottom: '20px' }}>
                                            {cartList.map((item, idx) => (
                                                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', borderBottom: '1px dashed #eee', paddingBottom: '5px' }}>
                                                    <span>{item.product_name} x {item.quantity} ({item.size})</span>
                                                    <strong>₹{(item.product_price || item.price) * item.quantity}</strong>
                                                </div>
                                            ))}
                                            <div style={{ marginTop: '10px', textAlign: 'right' }}>
                                                <strong>Total: ₹{cartList.reduce((acc, i) => acc + ((i.product_price || i.price) * i.quantity), 0)}</strong>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="checkout-item">
                                        <img src={selectedProduct.product_image ? `${BACKEND_URL}${selectedProduct.product_image}` : 'https://placehold.co/100x130?text=N/A'} />
                                        <div><strong>{selectedProduct.product_name}</strong><p>Size: {detailSize}</p><p>Qty: {detailQty}</p><p className="price">₹{selectedProduct.price}</p></div>
                                    </div>
                                )}

                                <div className="checkout-address">
                                    <h3>Select Delivery Address</h3>
                                    <div className="address-list">
                                        {/* Show currently selected custom address if it's not in the saved list */}
                                        {selectedAddress && !Object.values(user.address || {}).includes(selectedAddress) && (
                                            <div className="address-option active" style={{ border: '2px solid #007bff' }}>
                                                <strong>Custom Delivery Address</strong>
                                                <p>{selectedAddress}</p>
                                            </div>
                                        )}
                                        {Object.entries(user.address || {}).map(([label, full]) => (
                                            <div key={label} className={`address-option ${selectedAddress === full ? 'active' : ''}`} onClick={() => setSelectedAddress(full)}>
                                                <strong>{label}</strong>
                                                <p>{full}</p>
                                            </div>
                                        ))}
                                    </div>
                                    <button className="add-addr-btn" onClick={() => setShowAddressModal(true)}>+ Add New Address</button>
                                </div>
                                <div className="payment-options">
                                    <h3>Payment Method</h3>
                                    <div className="pay-grid">
                                        {['UPI', 'Card', 'COD'].map(method => (
                                            <button key={method} className={paymentMethod === method ? 'active' : ''} onClick={() => setPaymentMethod(method)}>{method === 'COD' ? 'Cash on Delivery' : method}</button>
                                        ))}
                                    </div>
                                </div>

                                <button className="confirm-order-btn" onClick={() => isBulkCheckout ? confirmBulkOrder() : handlePlaceOrder(selectedProduct.product_id, paymentMethod, selectedAddress, detailQty)}>
                                    Confirm {isBulkCheckout ? 'Bulk ' : ''}Order
                                    {/* Show total if bulk, or single price */}
                                    {isBulkCheckout
                                        ? ` ₹${cartList.reduce((sum, item) => sum + (item.price * item.quantity), 0)}`
                                        : ` ₹${selectedProduct ? selectedProduct.price * detailQty : 0}`
                                    }
                                </button>
                            </div>
                        </div>
                    )}

                    {currentView === 'wishlist' && (
                        <div className="view-container wishlist-view fade-in">
                            <h1>My Wishlist</h1>
                            {wishlist.length === 0 ? (
                                <div className="empty-state">
                                    <Heart size={48} color="#ddd" />
                                    <p>Your wishlist is empty</p>
                                    <button className="prime-btn" onClick={() => navigateToView('home')}>Go Shopping</button>
                                </div>
                            ) : (
                                <div className="auto-grid">
                                    {wishlist.map(p => {
                                        // Ensure p is an object, or find it in master products list if it's just an ID
                                        const prodIdStr = String(p.product_id || p);
                                        const prod = typeof p === 'object' && p.product_name ? p : products.find(op => String(op.product_id) === prodIdStr) || (typeof p === 'object' ? p : null);

                                        // If we still can't find details and p is just an ID, we can't render it properly
                                        if (!prod || !prod.product_name) return null;

                                        return (
                                            <div key={prod.product_id} className="auto-card">
                                                <div className="card-img-wrapper" onClick={() => handleProductClick(prod)}>
                                                    <img src={prod.product_image ? `${BACKEND_URL}${prod.product_image}` : 'https://placehold.co/300x400?text=N/A'} alt={prod.product_name} />
                                                </div>
                                                <div className="card-details">
                                                    <div className="price-row">
                                                        <h3>{prod.product_name}</h3>
                                                        <span className="price">₹{prod.price}</span>
                                                    </div>
                                                    <button className="wishlist-remove" onClick={() => toggleWishlist(prod)}>Remove</button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}

                    {currentView === 'cart' && (
                        <div className="view-container cart-view fade-in">
                            <h1>Shopping Cart</h1>
                            {cartList.length === 0 ? (
                                <div className="empty-state">
                                    <ShoppingCart size={48} color="#ddd" />
                                    <p>Your cart is empty</p>
                                    <button className="prime-btn" onClick={() => navigateToView('home')}>Go Shopping</button>
                                </div>
                            ) : (
                                <div className="cart-layout">
                                    <div className="cart-items">
                                        {cartList.map((item, idx) => (
                                            <div key={`${item.product_id}-${idx}`} className="cart-item-card">
                                                <img src={item.product_image ? `${BACKEND_URL}${item.product_image}` : 'https://placehold.co/80?text=N/A'} onClick={() => handleProductClick(item)} style={{ cursor: 'pointer' }} />
                                                <div className="item-info">
                                                    <h3 onClick={() => handleProductClick(item)} style={{ cursor: 'pointer' }}>{item.product_name}</h3>
                                                    <p>Size: {item.size}</p>
                                                    <div className="cart-qty-control">
                                                        <button onClick={() => handleUpdateCartQty(item, -1)} disabled={loading}><Minus size={14} /></button>
                                                        <span>{item.quantity}</span>
                                                        <button onClick={() => handleUpdateCartQty(item, 1)} disabled={loading}><Plus size={14} /></button>
                                                    </div>
                                                    <span className="price">₹{(item.product_price || item.price) * item.quantity}</span>
                                                </div>
                                                <button className="remove-btn" onClick={() => handleRemoveFromCart(item.cart_id)}><X size={18} /></button>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="cart-summary">
                                        <h3>Summary</h3>
                                        <div className="summary-row"><span>Subtotal</span><span>₹{cartList.reduce((acc, i) => acc + ((i.product_price || i.price) * i.quantity), 0)}</span></div>
                                        <div className="summary-row"><span>Delivery</span><span>Free</span></div>
                                        <div className="summary-row total"><span>Total</span><span>₹{cartList.reduce((acc, i) => acc + ((i.product_price || i.price) * i.quantity), 0)}</span></div>
                                        <button className="complete-btn" onClick={handleBulkCheckout}>Checkout All</button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {currentView === 'orders' && (
                        <div className="view-container orders-view fade-in">
                            <h1>My Orders</h1>
                            {ordersList.length === 0 ? (
                                <div className="empty-state">
                                    <Package size={48} color="#ddd" />
                                    <p>You haven't placed any orders yet</p>
                                    <button className="prime-btn" onClick={() => navigateToView('home')}>Start Shopping</button>
                                </div>
                            ) : (
                                <div className="orders-list">
                                    {ordersList.map(order => (
                                        <div key={order.order_id} className={`order-history-card ${order.order_status === 'cancelled' ? 'cancelled' : ''}`}>
                                            <div className="order-main">
                                                <img src={order.product_details?.product_image ? `${BACKEND_URL}${order.product_details.product_image}` : 'https://placehold.co/80?text=N/A'} alt="Order" />
                                                <div className="order-info">
                                                    <div className="order-header-row">
                                                        <span className="order-id">#{order.order_id}</span>
                                                        <div className={`status-pill ${order.order_status}`}>{order.order_status}</div>
                                                    </div>
                                                    <h3>{order.product_details?.product_name || 'Product'}</h3>
                                                    <p>Qty: {order.quantity} | {order.payment_method}</p>
                                                </div>
                                                <div className="order-actions">
                                                    <span className="order-price">₹{order.total_amount}</span>
                                                    <button
                                                        className={`cancel-order-btn ${order.order_status === 'cancelled' ? 'cancelled-view' : ''}`}
                                                        onClick={() => (order.order_status === 'placed' || order.order_status === 'processing') && handleCancelOrder(order.order_id)}
                                                        disabled={order.order_status === 'cancelled'}
                                                    >
                                                        {order.order_status === 'cancelled' ? 'Cancelled' : 'Cancel'}
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="order-footer">
                                                <div className="footer-left">
                                                    <span className="footer-ordered-text">Ordered: {new Date(order.created_at).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                                                    {order.order_status !== 'cancelled' && (
                                                        <span className="footer-delivery-text"> | Expected: {order.expected_delivery_date}</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {currentView === 'success' && orderStatus && (
                        <div className="view-container success-view scale-in">
                            <div className="success-icon"><CheckCircle size={80} /></div>
                            <h1>Order Placed Successfully</h1>
                            {orderStatus.bulk ? (
                                <div className="success-details">
                                    <p>Your bulk order with <strong>{orderStatus.item_count} items</strong> has been confirmed.</p>
                                    <p>Total amount: <strong>₹{orderStatus.total_amount}</strong></p>
                                    <p className="order-ids">Order IDs: {orderStatus.order_ids.join(', ')}</p>
                                </div>
                            ) : (
                                <div className="order-receipt">
                                    <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                                        <img src={orderStatus.product_image ? `${BACKEND_URL}${orderStatus.product_image}` : 'https://placehold.co/100x130?text=Product'} style={{ width: '80px', borderRadius: '10px' }} alt="Product" />
                                    </div>
                                    <div className="receipt-row"><span>Order ID</span> <strong>#{orderStatus.order_id}</strong></div>
                                    <div className="receipt-row"><span>Product</span> <strong>{orderStatus.product_name} ({orderStatus.product_size})</strong></div>
                                    <div className="receipt-row"><span>Quantity</span> <strong>{orderStatus.quantity}</strong></div>
                                    <div className="receipt-row"><span>Price/Item</span> <strong>₹{orderStatus.price_per_item}</strong></div>
                                    <div className="receipt-row" style={{ marginTop: '10px', paddingTop: '10px', borderTop: '2px solid #edff55' }}><span>Total Amount</span> <strong style={{ fontSize: '1.2rem' }}>₹{orderStatus.total}</strong></div>
                                    <div className="receipt-row"><span>Payment</span> <strong>{orderStatus.payment_method}</strong></div>
                                    <div className="receipt-row full"><span>Delivery Address</span> <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px', lineHeight: '1.4' }}>{orderStatus.address}</p></div>
                                </div>
                            )}
                            <button className="prime-btn" onClick={() => { setProducts([]); navigateToView('home'); setHasInteracted(false); setHistoryStack(['home']); }}>Shop More</button>
                        </div>
                    )}
                </section>

                <div className="ai-feedback-bar"><MessageSquare size={18} /><p>{aiMessage || "Ready to assist you."}</p></div>
            </main>

            {
                showAddressModal && (
                    <div className="address-modal-overlay">
                        <div className="address-modal">
                            <h3>Delivery Addresses</h3>

                            {/* 1. Show existing addresses */}
                            <div className="existing-addresses-list" style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '15px' }}>
                                {Object.keys(user.address || {}).length > 0 ? (
                                    Object.entries(user.address).map(([label, text]) => (
                                        <div key={label} className="saved-addr-item" style={{ padding: '10px', background: '#f9f9f9', borderRadius: '10px', marginBottom: '8px', border: '1px solid #eee' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <strong style={{ fontSize: '0.9rem', color: '#000' }}>{label}</strong>
                                                <span style={{ fontSize: '0.7rem', background: '#edff55', padding: '2px 6px', borderRadius: '4px', fontWeight: '800' }}>SAVED</span>
                                            </div>
                                            <p style={{ margin: '5px 0 0', fontSize: '0.8rem', color: '#666', lineHeight: '1.4' }}>{text}</p>
                                        </div>
                                    ))
                                ) : (
                                    <p style={{ textAlign: 'center', color: '#888', fontStyle: 'italic' }}>No addresses saved yet.</p>
                                )}
                            </div>

                            {/* 2. Add new address form */}
                            <div className="add-address-form">
                                <h4 style={{ marginBottom: '10px' }}>Add New Address</h4>
                                <label>Address Label (e.g., Home, Work, Kadapa)</label>
                                <input className="modal-input" type="text" value={addressLabel} onChange={(e) => setAddressLabel(e.target.value)} placeholder="Home" />
                                <label>Full Address</label>
                                <textarea value={addressText} onChange={(e) => setAddressText(e.target.value)} placeholder="Full street address..." />

                                <div className="modal-btns">
                                    <button onClick={() => setShowAddressModal(false)}>Cancel</button>
                                    <button className="save" onClick={saveAddress}>Save Address</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )
            }

            {
                showAgentInfo && selectedAgent && (
                    <div className="address-modal-overlay">
                        <div className="address-modal">
                            <div className="modal-header">
                                <h3>{selectedAgent.title}</h3>
                                <button className="close-btn" onClick={() => setShowAgentInfo(false)}><X size={20} /></button>
                            </div>
                            <div className="agent-desc">
                                {selectedAgent.lines.map((line, idx) => (
                                    <p key={idx} style={{ marginBottom: '8px', paddingLeft: '10px', borderLeft: '3px solid #edff55' }}>
                                        {line}
                                    </p>
                                ))}
                            </div>
                            <button className="prime-btn" style={{ width: '100%', marginTop: '20px' }} onClick={() => setShowAgentInfo(false)}>Got it</button>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default Home;
