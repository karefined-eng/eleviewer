// google_apps_script_products_generator.gs
// Elevon Prospera Products.json Generator
// Uses OpenRouter API (NOT Gemini) for image analysis - better rate limits, unlimited daily choice


const CONFIG = {
  GOOGLE_DRIVE_FOLDER_ID: "1PBvoJpkgL__507KuBvO4OKe6A4icXNrt",
  OPENROUTER_API_KEY: "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",
  OPENROUTER_MODEL: "qwen/qwen2.5-vl-72b-instruct:free", // Best free vision model - 72B parameters, $0 cost
  DEFAULT_PRICE: 220,
  DEFAULT_PRICE_DISCOUNTED: 200,
  BUSINESS_NAME: "Very Nice Concepts",
  BUSINESS_LOCATION: "Teshie, Accra",// google_apps_script_products_generator.gs
// EleAutoScript v2 - Uses Google Gemini API (FREE, NO CREDIT CARD)
// Reads images from Google Drive folder, analyzes with Gemini 2.0 Flash Vision, generates SEO-optimized products.json


const CONFIG = {
  GOOGLE_DRIVE_FOLDER_ID: "YOUR_DRIVE_FOLDER_ID_HERE",
  GEMINI_API_KEY: "YOUR_GEMINI_API_KEY_HERE",
  GEMINI_MODEL: "gemini-2.0-flash",
  DEFAULT_PRICE: 220,
  DEFAULT_PRICE_DISCOUNTED: 180,
  BUSINESS_NAME: "Very Nice Concepts",
  BUSINESS_LOCATION: "Teshie, Accra",
  CURRENCY: "GHS",
  REQUEST_DELAY_MS: 3500 // 3.5 seconds between requests (respects rate limits)
};


function generateProductsJson() {
  console.log("[INFO] Starting products.json generation (Gemini API - FREE)...");
  
  try {
    // Step 1: Get images from Drive folder
    const images = getImagesFromFolder(CONFIG.GOOGLE_DRIVE_FOLDER_ID);
    console.log(`[INFO] Found ${images.length} images in folder`);
    
    if (images.length === 0) {
      console.log("[ERROR] No images found in the specified folder");
      return;
    }


    // Step 2: Analyze each image with Gemini Vision API
    const products = [];
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      const imageName = image.getName();
      console.log(`[INFO] Processing image ${i + 1}/${images.length}: ${imageName}`);
      
      try {
        const imageData = getImageAsBase64(image);
        const mimeType = getImageMimeType(imageName);
        const analysis = analyzeImageWithGemini(imageData, mimeType);
        
        if (!analysis) {
          console.log(`[WARNING] No analysis returned for ${imageName}, skipping...`);
          continue;
        }
        
        // Step 3: Generate product object
        const product = {
          id: i + 1,
          title: generateTitle(analysis),
          price: determinePrice(analysis),
          description: generateDescription(analysis),
          tags: generateHighIntentTags(analysis)
        };
        
        products.push(product);
        console.log(`[INFO] ✅ Generated product ${i + 1}: "${product.title}"`);
        
        // Rate limiting: 3.5 second delay between API calls
        Utilities.sleep(CONFIG.REQUEST_DELAY_MS);
        
      } catch (imageError) {
        console.log(`[ERROR] Failed to process ${imageName}: ${imageError.message}`);
        continue;
      }
    }


    // Step 4: Save products.json to Drive
    const fileName = `products_${new Date().toISOString().split('T')[0]}.json`;
    const jsonContent = JSON.stringify(products, null, 2);
    saveJsonToDrive(fileName, jsonContent, CONFIG.GOOGLE_DRIVE_FOLDER_ID);
    
    console.log(`[INFO] ✅ Successfully generated ${products.length} products`);
    console.log(`[INFO] File saved: ${fileName}`);
    
  } catch (error) {
    console.log(`[CRITICAL ERROR] ${error.message}`);
    throw error;
  }
}


function getImagesFromFolder(folderId) {
  const folder = DriveApp.getFolderById(folderId);
  const files = folder.getFiles();
  const images = [];
  
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
  
  while (files.hasNext()) {
    const file = files.next();
    const fileName = file.getName().toLowerCase();
    const hasImageExtension = imageExtensions.some(ext => fileName.endsWith(ext));
    
    if (hasImageExtension) {
      images.push(file);
    }
  }
  
  return images;
}


function getImageAsBase64(file) {
  const blob = file.getBlob();
  const bytes = blob.getBytes();
  return Utilities.base64Encode(bytes);
}


function getImageMimeType(fileName) {
  const ext = fileName.toLowerCase().split('.').pop();
  const mimeTypes = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp'
  };
  return mimeTypes[ext] || 'image/jpeg';
}


function analyzeImageWithGemini(imageBase64, mimeType) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.GEMINI_MODEL}:generateContent?key=${CONFIG.GEMINI_API_KEY}`;
  
  const payload = {
    contents: [{
      parts: [
        {
          text: `You are a fashion product analyst for a handmade leather goods business in Ghana. Analyze this product image and provide:


1. COLOR: Primary color(s) of the product
2. MATERIAL: Material (leather type, texture)
3. STYLE: Style category (casual, formal, luxury, vintage, contemporary)
4. FEATURES: Key distinguishing features (embroidery, buckles, patterns, embossing, etc.)
5. OCCASION: Best use occasions
6. SIZE_RANGE: Typical size range (e.g., 38-45 for shoes)


Format your response EXACTLY as:
COLOR: [color]
MATERIAL: [material]
STYLE: [style]
FEATURES: [feature1, feature2, feature3]
OCCASION: [occasion1, occasion2]
SIZE_RANGE: [range]`
        },
        {
          inline_data: {
            mime_type: mimeType,
            data: imageBase64
          }
        }
      ]
    }]
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const result = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200) {
    console.log("[DEBUG] Gemini Response:", response.getContentText());
    throw new Error(`Gemini API Error: ${result.error?.message || 'Unknown error'}`);
  }
  
  const text = result.candidates[0].content.parts[0].text;
  return parseGeminiResponse(text);
}


function parseGeminiResponse(text) {
  const analysis = {
    color: extractField(text, 'COLOR'),
    material: extractField(text, 'MATERIAL'),
    style: extractField(text, 'STYLE'),
    features: extractField(text, 'FEATURES').split(',').map(f => f.trim()).filter(f => f),
    occasion: extractField(text, 'OCCASION').split(',').map(o => o.trim()).filter(o => o),
    sizeRange: extractField(text, 'SIZE_RANGE')
  };
  
  return analysis;
}


function extractField(text, fieldName) {
  const regex = new RegExp(`${fieldName}:\\s*(.+?)(?=\\n|$)`, 'i');
  const match = text.match(regex);
  return match ? match[1].trim() : '';
}


function generateTitle(analysis) {
  const { color, material, features } = analysis;
  const primaryFeature = features && features.length > 0 ? features[0] : 'Slides';
  
  // Format: "[Color] [Material] [Primary Feature]"
  const title = `${color} ${material} ${primaryFeature}`.trim();
  
  // Capitalize each word
  return title.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ').substring(0, 75);
}


function determinePrice(analysis) {
  // Premium pricing for luxury/formal styles with premium features
  const isLuxury = analysis.style && analysis.style.toLowerCase().includes('luxury');
  const isFormal = analysis.style && analysis.style.toLowerCase().includes('formal');
  const hasEmbroidery = analysis.features && analysis.features.some(f => f.toLowerCase().includes('embroid'));
  const hasCrocodile = analysis.material && analysis.material.toLowerCase().includes('crocodile');
  
  if (hasCrocodile) return 240; // Crocodile pattern premium
  if (isLuxury || (isFormal && hasEmbroidery)) return 220;
  if (analysis.style && analysis.style.toLowerCase().includes('casual')) return 180;
  
  return CONFIG.DEFAULT_PRICE;
}


function generateDescription(analysis) {
  const { color, material, style, features, occasion } = analysis;
  
  let description = `Premium ${color} ${material} ${style} footwear featuring ${features.join(', ')}.\n\n`;
  
  if (occasion && occasion.length > 0) {
    description += `Perfect for: ${occasion.join(', ')}\n\n`;
  }
  
  description += `✓ 100% ${material || 'genuine leather'}\n`;
  description += `✓ Handmade in ${CONFIG.BUSINESS_LOCATION}\n`;
  description += `✓ Durable construction\n`;
  description += `✓ Available in sizes ${analysis.sizeRange || '38-45'}\n\n`;
  description += `Crafted with traditional artisan techniques by ${CONFIG.BUSINESS_NAME}.`;
  
  return description;
}


function generateHighIntentTags(analysis) {
  const tags = new Set();
  const { color, material, style, features, occasion, sizeRange } = analysis;
  
  // Core product tags
  if (color && material) {
    tags.add(`${color.toLowerCase()} ${material.toLowerCase()}`);
    tags.add(`${color.toLowerCase()} leather slides`);
    tags.add(`handmade ${color.toLowerCase()} shoes`);
  }
  
  // Material-based tags
  if (material && material.toLowerCase().includes('leather')) {
    tags.add('genuine leather sandals');
    tags.add('premium leather footwear');
    tags.add('handmade leather slippers');
    tags.add('100% leather shoes');
  }
  
  // Style-based tags
  if (style) {
    tags.add(`${style.toLowerCase()} footwear`);
    tags.add(`${style.toLowerCase()} slides`);
    tags.add(`${style.toLowerCase()} leather shoes`);
  }
  
  // Feature-based tags
  if (features && features.length > 0) {
    features.forEach(feature => {
      const feat = feature.toLowerCase().trim();
      if (feat.length > 0) {
        if (feat.includes('buckle') || feat.includes('emblem') || feat.includes('embroid')) {
          tags.add(`${feat} shoes`);
          tags.add('decorated leather slides');
          tags.add('statement leather shoes');
        }
        if (feat.includes('crocodile') || feat.includes('textured') || feat.includes('pattern')) {
          tags.add(`${feat} leather`);
          tags.add('premium patterned shoes');
          tags.add('textured leather slides');
        }
      }
    });
  }
  
  // Occasion-based tags
  if (occasion && occasion.length > 0) {
    occasion.forEach(occ => {
      const o = occ.toLowerCase().trim();
      if (o.length > 0) {
        tags.add(`${o} shoes Ghana`);
        tags.add(`${o} leather slippers`);
        tags.add(`${o} footwear`);
      }
    });
  }
  
  // Local/SEO intent tags (high priority)
  tags.add(`handmade slippers ${CONFIG.BUSINESS_LOCATION}`);
  tags.add('artisan leather shoes Ghana');
  tags.add(`leather slippers ${CONFIG.BUSINESS_LOCATION}`);
  tags.add('premium footwear Ghana');
  tags.add('handcrafted shoes Accra');
  tags.add('local artisan footwear');
  tags.add('authentic leather slides');
  tags.add('quality handmade shoes');
  tags.add("men's leather slippers Ghana");
  tags.add('Ghana handmade leather');
  tags.add('Accra leather shoes');
  tags.add('Teshie crafted footwear');
  
  // High-volume search intent tags
  tags.add('leather shoes online');
  tags.add('affordable premium footwear');
  tags.add('best leather slippers');
  tags.add('custom handmade shoes');
  tags.add('durable leather sandals');
  tags.add('luxury footwear');
  tags.add('artisan shoes');
  
  // Return top 20 tags
  return Array.from(tags).slice(0, 20);
}


function saveJsonToDrive(fileName, jsonContent, folderId) {
  const folder = DriveApp.getFolderById(folderId);
  const blob = Utilities.newBlob(jsonContent, 'application/json', fileName);
  folder.createFile(blob);
}


// Manual trigger function (call this from Apps Script editor)
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('EleAutoScript')
    .addItem('Generate products.json (Gemini API FREE)', 'generateProductsJson')
    .addToUi();
}
  CURRENCY: "GHS",
  REQUEST_DELAY_MS: 3500 // 3.5 seconds between requests (respects 20 req/min limit)
};


function generateProductsJson() {
  console.log("[INFO] Starting products.json generation pipeline (OpenRouter)...");
  
  try {
    // Step 1: Get images from Drive folder
    const images = getImagesFromFolder(CONFIG.GOOGLE_DRIVE_FOLDER_ID);
    console.log(`[INFO] Found ${images.length} images in folder`);
    
    if (images.length === 0) {
      console.log("[ERROR] No images found in the specified folder");
      return;
    }


    // Step 2: Analyze each image with OpenRouter (Gemini 2.0 via OpenRouter)
    const products = [];
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      const imageName = image.getName();
      console.log(`[INFO] Processing image ${i + 1}/${images.length}: ${imageName}`);
      
      try {
        const imageData = getImageAsBase64(image);
        const mimeType = getImageMimeType(imageName);
        const analysis = analyzeImageWithOpenRouter(imageData, mimeType, imageName);
        
        // Step 3: Generate product object
        const product = {
          id: i + 1,
          title: generateTitle(analysis),
          price: determinePrice(analysis),
          description: generateDescription(analysis),
          tags: generateHighIntentTags(analysis)
        };
        
        products.push(product);
        console.log(`[INFO] ✅ Generated product ${i + 1}: "${product.title}"`);
        
        // Rate limiting: 1 second delay between API calls (OpenRouter is efficient)
        Utilities.sleep(CONFIG.REQUEST_DELAY_MS);
        
      } catch (imageError) {
        console.log(`[ERROR] Failed to process ${imageName}: ${imageError.message}`);
        continue;
      }
    }


    // Step 4: Save products.json to Drive
    const fileName = `products_${new Date().toISOString().split('T')[0]}.json`;
    const jsonContent = JSON.stringify(products, null, 2);
    saveJsonToDrive(fileName, jsonContent, CONFIG.GOOGLE_DRIVE_FOLDER_ID);
    
    console.log(`[INFO] ✅ Successfully generated ${products.length} products`);
    console.log(`[INFO] File saved: ${fileName}`);
    
  } catch (error) {
    console.log(`[CRITICAL ERROR] ${error.message}`);
    throw error;
  }
}


function getImagesFromFolder(folderId) {
  const folder = DriveApp.getFolderById(folderId);
  const files = folder.getFiles();
  const images = [];
  
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
  
  while (files.hasNext()) {
    const file = files.next();
    const fileName = file.getName().toLowerCase();
    const hasImageExtension = imageExtensions.some(ext => fileName.endsWith(ext));
    
    if (hasImageExtension) {
      images.push(file);
    }
  }
  
  return images;
}


function getImageAsBase64(file) {
  const blob = file.getBlob();
  const bytes = blob.getBytes();
  return Utilities.base64Encode(bytes);
}


function getImageMimeType(fileName) {
  const ext = fileName.toLowerCase().split('.').pop();
  const mimeTypes = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp'
  };
  return mimeTypes[ext] || 'image/jpeg';
}


function analyzeImageWithOpenRouter(imageBase64, mimeType, imageName) {
  const url = "https://openrouter.ai/api/v1/messages";
  
  const payload = {
    model: CONFIG.OPENROUTER_MODEL,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: `You are a fashion product analyst for a handmade leather goods business in Ghana. Analyze this product image and provide:


1. COLOR: Primary color(s) of the product
2. MATERIAL: Material (leather type, texture)
3. STYLE: Style category (casual, formal, luxury, vintage, contemporary)
4. FEATURES: Key distinguishing features (embroidery, buckles, patterns, embossing, etc.)
5. OCCASION: Best use occasions
6. SIZE_RANGE: Typical size range (e.g., 38-45 for shoes)


Format your response EXACTLY as:
COLOR: [color]
MATERIAL: [material]
STYLE: [style]
FEATURES: [feature1, feature2, feature3]
OCCASION: [occasion1, occasion2]
SIZE_RANGE: [range]`
          },
          {
            type: "image",
            source: {
              type: "base64",
              media_type: mimeType,
              data: imageBase64
            }
          }
        ]
      }
    ]
  };
  
  const options = {
    method: 'post',
    headers: {
      "Authorization": `Bearer ${CONFIG.OPENROUTER_API_KEY}`,
      "HTTP-Referer": "https://elevon-prospera.com",
      "X-Title": "Elevon Prospera Products Generator"
    },
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const result = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200) {
    console.log("[DEBUG] OpenRouter Response:", response.getContentText());
    throw new Error(`OpenRouter API Error: ${result.error?.message || 'Unknown error'}`);
  }
  
  const text = result.content[0].text;
  return parseGeminiResponse(text);
}


function parseGeminiResponse(text) {
  const analysis = {
    color: extractField(text, 'COLOR'),
    material: extractField(text, 'MATERIAL'),
    style: extractField(text, 'STYLE'),
    features: extractField(text, 'FEATURES').split(',').map(f => f.trim()).filter(f => f),
    occasion: extractField(text, 'OCCASION').split(',').map(o => o.trim()).filter(o => o),
    sizeRange: extractField(text, 'SIZE_RANGE')
  };
  
  return analysis;
}


function extractField(text, fieldName) {
  const regex = new RegExp(`${fieldName}:\\s*(.+?)(?=\\n|$)`, 'i');
  const match = text.match(regex);
  return match ? match[1].trim() : '';
}


function generateTitle(analysis) {
  const { color, material, features } = analysis;
  const primaryFeature = features && features.length > 0 ? features[0] : 'Slides';
  
  // Format: "[Color] [Material] [Primary Feature]"
  const title = `${color} ${material} ${primaryFeature}`.trim();
  
  // Capitalize each word
  return title.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ').substring(0, 75);
}


function determinePrice(analysis) {
  // Premium pricing for luxury/formal styles with premium features
  const isLuxury = analysis.style && analysis.style.toLowerCase().includes('luxury');
  const isFormal = analysis.style && analysis.style.toLowerCase().includes('formal');
  const hasEmbroidery = analysis.features && analysis.features.some(f => f.toLowerCase().includes('embroid'));
  const hasCrocodile = analysis.material && analysis.material.toLowerCase().includes('crocodile');
  
  if (hasCrocodile) return 240; // Crocodile pattern premium
  if (isLuxury || (isFormal && hasEmbroidery)) return 220;
  if (analysis.style && analysis.style.toLowerCase().includes('casual')) return 180;
  
  return CONFIG.DEFAULT_PRICE;
}


function generateDescription(analysis) {
  const { color, material, style, features, occasion } = analysis;
  
  let description = `Premium ${color} ${material} ${style} footwear featuring ${features.join(', ')}.\n\n`;
  
  if (occasion && occasion.length > 0) {
    description += `Perfect for: ${occasion.join(', ')}\n\n`;
  }
  
  description += `✓ 100% ${material || 'genuine leather'}\n`;
  description += `✓ Handmade in ${CONFIG.BUSINESS_LOCATION}\n`;
  description += `✓ Durable construction\n`;
  description += `✓ Available in sizes ${analysis.sizeRange || '38-45'}\n\n`;
  description += `Crafted with traditional artisan techniques by ${CONFIG.BUSINESS_NAME}.`;
  
  return description;
}


function generateHighIntentTags(analysis) {
  const tags = new Set();
  const { color, material, style, features, occasion, sizeRange } = analysis;
  
  // Core product tags
  if (color && material) {
    tags.add(`${color.toLowerCase()} ${material.toLowerCase()}`);
    tags.add(`${color.toLowerCase()} leather slides`);
    tags.add(`handmade ${color.toLowerCase()} shoes`);
  }
  
  // Material-based tags
  if (material && material.toLowerCase().includes('leather')) {
    tags.add('genuine leather sandals');
    tags.add('premium leather footwear');
    tags.add('handmade leather slippers');
    tags.add('100% leather shoes');
  }
  
  // Style-based tags
  if (style) {
    tags.add(`${style.toLowerCase()} footwear`);
    tags.add(`${style.toLowerCase()} slides`);
    tags.add(`${style.toLowerCase()} leather shoes`);
  }
  
  // Feature-based tags
  if (features && features.length > 0) {
    features.forEach(feature => {
      const feat = feature.toLowerCase().trim();
      if (feat.length > 0) {
        if (feat.includes('buckle') || feat.includes('emblem') || feat.includes('embroid')) {
          tags.add(`${feat} shoes`);
          tags.add('decorated leather slides');
          tags.add('statement leather shoes');
        }
        if (feat.includes('crocodile') || feat.includes('textured') || feat.includes('pattern')) {
          tags.add(`${feat} leather`);
          tags.add('premium patterned shoes');
          tags.add('textured leather slides');
        }
      }
    });
  }
  
  // Occasion-based tags
  if (occasion && occasion.length > 0) {
    occasion.forEach(occ => {
      const o = occ.toLowerCase().trim();
      if (o.length > 0) {
        tags.add(`${o} shoes Ghana`);
        tags.add(`${o} leather slippers`);
        tags.add(`${o} footwear`);
      }
    });
  }
  
  // Local/SEO intent tags (high priority)
  tags.add(`handmade slippers ${CONFIG.BUSINESS_LOCATION}`);
  tags.add('artisan leather shoes Ghana');
  tags.add(`leather slippers ${CONFIG.BUSINESS_LOCATION}`);
  tags.add('premium footwear Ghana');
  tags.add('handcrafted shoes Accra');
  tags.add('local artisan footwear');
  tags.add('authentic leather slides');
  tags.add('quality handmade shoes');
  tags.add("men's leather slippers Ghana");
  tags.add('Ghana handmade leather');
  tags.add('Accra leather shoes');
  tags.add('Teshie crafted footwear');
  
  // High-volume search intent tags
  tags.add('leather shoes online');
  tags.add('affordable premium footwear');
  tags.add('best leather slippers');
  tags.add('custom handmade shoes');
  tags.add('durable leather sandals');
  tags.add('luxury footwear');
  tags.add('artisan shoes');
  
  // Return top 20 tags
  return Array.from(tags).slice(0, 20);
}


function saveJsonToDrive(fileName, jsonContent, folderId) {
  const folder = DriveApp.getFolderById(folderId);
  const blob = Utilities.newBlob(jsonContent, 'application/json', fileName);
  folder.createFile(blob);
}


// Manual trigger function (call this from Apps Script editor)
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Elevon Products Generator')
    .addItem('Generate products.json (OpenRouter)', 'generateProductsJson')
    .addToUi();
}