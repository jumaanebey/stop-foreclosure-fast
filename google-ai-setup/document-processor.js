/**
 * DOCUMENT PROCESSING WORKFLOW
 * Automatically extracts data from foreclosure documents
 */

const { DocumentProcessorServiceClient } = require('@google-cloud/documentai');
const { Storage } = require('@google-cloud/storage');
const { VertexAI } = require('@google-cloud/vertexai');

// Initialize clients
const documentAI = new DocumentProcessorServiceClient();
const storage = new Storage();
const bucketName = 'foreclosure-documents';

// Vertex AI for document analysis
const vertexAI = new VertexAI({
    project: 'foreclosure-ai-assistant',
    location: 'us-central1',
});

const geminiModel = vertexAI.preview.getGenerativeModel({
    model: 'gemini-1.5-pro',
});

/**
 * Main Document Processing Pipeline
 */
class ForeclosureDocumentProcessor {
    constructor() {
        this.processorPath = 'projects/foreclosure-ai-assistant/locations/us/processors/YOUR_PROCESSOR_ID';
    }

    /**
     * Process uploaded foreclosure document
     */
    async processDocument(filePath, documentType) {
        console.log(`Processing ${documentType}: ${filePath}`);

        // Step 1: Extract text and data with Document AI
        const extractedData = await this.extractWithDocumentAI(filePath);

        // Step 2: Analyze with Gemini for insights
        const analysis = await this.analyzeWithGemini(extractedData, documentType);

        // Step 3: Structure and validate data
        const structuredData = await this.structureData(analysis, documentType);

        // Step 4: Generate action items
        const actionItems = await this.generateActionItems(structuredData);

        return {
            extractedData,
            analysis,
            structuredData,
            actionItems,
            processedAt: new Date().toISOString()
        };
    }

    /**
     * Extract data using Document AI
     */
    async extractWithDocumentAI(filePath) {
        const request = {
            name: this.processorPath,
            rawDocument: {
                content: await this.getFileContent(filePath),
                mimeType: 'application/pdf',
            },
        };

        const [result] = await documentAI.processDocument(request);
        const { document } = result;

        // Extract key entities
        const entities = {};
        if (document.entities) {
            document.entities.forEach(entity => {
                entities[entity.type] = entity.mentionText;
            });
        }

        return {
            text: document.text,
            entities,
            pages: document.pages ? document.pages.length : 0,
            confidence: document.pages?.[0]?.confidence || 0,
        };
    }

    /**
     * Analyze document with Gemini AI
     */
    async analyzeWithGemini(extractedData, documentType) {
        const prompts = {
            'notice_of_default': `
                Analyze this Notice of Default and extract:
                1. Recording date
                2. Amount in default
                3. Trustee information
                4. Property address
                5. Deadline to cure default
                6. Total amount owed
                7. Monthly payment amount
                8. Lender/beneficiary details

                Also determine:
                - Days until auction
                - Is this a first or second mortgage?
                - Any junior liens mentioned?
                - Recommended immediate actions

                Document text: ${extractedData.text}
            `,
            'notice_of_sale': `
                Analyze this Notice of Trustee Sale and extract:
                1. Sale date and time
                2. Sale location
                3. Opening bid amount
                4. Property legal description
                5. APN (Assessor Parcel Number)
                6. Trustee contact information
                7. Publication dates

                Calculate:
                - Days until sale
                - Estimated equity (if property value available)
                - Urgency level (1-10)

                Document text: ${extractedData.text}
            `,
            'mortgage_statement': `
                Analyze this mortgage statement and extract:
                1. Current balance
                2. Monthly payment amount
                3. Past due amount
                4. Late fees
                5. Escrow balance
                6. Interest rate
                7. Payment history

                Identify:
                - Months behind
                - Total to reinstate
                - Any loss mitigation offers mentioned

                Document text: ${extractedData.text}
            `,
        };

        const prompt = prompts[documentType] || `
            Analyze this foreclosure-related document and extract all relevant
            dates, amounts, parties, and deadlines. Document: ${extractedData.text}
        `;

        const result = await geminiModel.generateContent({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
        });

        const response = await result.response;
        return JSON.parse(response.text().replace(/```json\n?|\n?```/g, ''));
    }

    /**
     * Structure extracted data into standardized format
     */
    async structureData(analysis, documentType) {
        const baseStructure = {
            documentType,
            uploadedAt: new Date().toISOString(),
            status: 'processed',
        };

        switch (documentType) {
            case 'notice_of_default':
                return {
                    ...baseStructure,
                    recordingDate: analysis.recordingDate,
                    defaultAmount: this.parseAmount(analysis.amountInDefault),
                    totalOwed: this.parseAmount(analysis.totalAmountOwed),
                    cureDeadline: this.parseDate(analysis.deadlineToCure),
                    daysToAuction: analysis.daysUntilAuction,
                    trustee: analysis.trusteeInformation,
                    propertyAddress: analysis.propertyAddress,
                    urgencyScore: this.calculateUrgency(analysis.daysUntilAuction),
                };

            case 'notice_of_sale':
                return {
                    ...baseStructure,
                    saleDate: this.parseDate(analysis.saleDate),
                    saleLocation: analysis.saleLocation,
                    openingBid: this.parseAmount(analysis.openingBid),
                    propertyAPN: analysis.apn,
                    daysUntilSale: analysis.daysUntilSale,
                    urgencyScore: 10, // Maximum urgency for sale notices
                };

            case 'mortgage_statement':
                return {
                    ...baseStructure,
                    currentBalance: this.parseAmount(analysis.currentBalance),
                    monthlyPayment: this.parseAmount(analysis.monthlyPayment),
                    pastDueAmount: this.parseAmount(analysis.pastDueAmount),
                    monthsBehind: analysis.monthsBehind,
                    reinstateAmount: this.parseAmount(analysis.totalToReinstate),
                    urgencyScore: this.calculateUrgency(analysis.monthsBehind * 30),
                };

            default:
                return { ...baseStructure, ...analysis };
        }
    }

    /**
     * Generate actionable next steps
     */
    async generateActionItems(structuredData) {
        const actions = [];
        const { urgencyScore, documentType } = structuredData;

        // Critical urgency actions (score 9-10)
        if (urgencyScore >= 9) {
            actions.push({
                priority: 'CRITICAL',
                action: 'Contact homeowner immediately',
                deadline: 'Within 2 hours',
                assignTo: 'Senior Specialist',
            });
            actions.push({
                priority: 'CRITICAL',
                action: 'Prepare emergency postponement request',
                deadline: 'Today',
                assignTo: 'Legal Team',
            });
        }

        // Document-specific actions
        if (documentType === 'notice_of_default') {
            actions.push({
                priority: 'HIGH',
                action: 'Calculate reinstatement amount',
                deadline: 'Within 24 hours',
                details: `Default amount: $${structuredData.defaultAmount}`,
            });
            actions.push({
                priority: 'HIGH',
                action: 'Contact lender for modification options',
                deadline: 'Within 48 hours',
            });
        }

        if (documentType === 'notice_of_sale') {
            actions.push({
                priority: 'CRITICAL',
                action: 'File postponement if possible',
                deadline: 'Immediately',
                details: `Sale date: ${structuredData.saleDate}`,
            });
            actions.push({
                priority: 'CRITICAL',
                action: 'Prepare cash offer or short sale package',
                deadline: 'Within 24 hours',
            });
        }

        // Generate personalized action plan with Gemini
        const geminiActions = await this.generateGeminiActionPlan(structuredData);
        actions.push(...geminiActions);

        return actions;
    }

    /**
     * Use Gemini to generate smart action plan
     */
    async generateGeminiActionPlan(data) {
        const prompt = `
        Based on this foreclosure situation, generate a prioritized action plan:

        Document Type: ${data.documentType}
        Urgency Score: ${data.urgencyScore}/10
        ${data.daysUntilSale ? `Days until sale: ${data.daysUntilSale}` : ''}
        ${data.defaultAmount ? `Default amount: $${data.defaultAmount}` : ''}

        Generate 3-5 specific, actionable steps the homeowner should take.
        Format as JSON array with: action, timeline, expectedOutcome, resources
        `;

        const result = await geminiModel.generateContent({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
        });

        const response = await result.response;
        const actions = JSON.parse(response.text().replace(/```json\n?|\n?```/g, ''));

        return actions.map(action => ({
            priority: 'AI_RECOMMENDED',
            ...action,
        }));
    }

    /**
     * Helper methods
     */
    async getFileContent(filePath) {
        const file = storage.bucket(bucketName).file(filePath);
        const [content] = await file.download();
        return Buffer.from(content).toString('base64');
    }

    parseAmount(amountStr) {
        if (!amountStr) return 0;
        return parseFloat(amountStr.replace(/[$,]/g, ''));
    }

    parseDate(dateStr) {
        if (!dateStr) return null;
        return new Date(dateStr).toISOString();
    }

    calculateUrgency(daysRemaining) {
        if (daysRemaining <= 7) return 10;
        if (daysRemaining <= 14) return 9;
        if (daysRemaining <= 30) return 8;
        if (daysRemaining <= 60) return 6;
        if (daysRemaining <= 90) return 4;
        return 2;
    }
}

/**
 * Express endpoint for document upload
 */
const express = require('express');
const multer = require('multer');
const app = express();

const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
});

app.post('/api/process-document', upload.single('document'), async (req, res) => {
    try {
        const { documentType = 'auto-detect' } = req.body;
        const file = req.file;

        if (!file) {
            return res.status(400).json({ error: 'No document uploaded' });
        }

        // Upload to Cloud Storage
        const fileName = `${Date.now()}-${file.originalname}`;
        const fileUpload = storage.bucket(bucketName).file(fileName);
        await fileUpload.save(file.buffer);

        // Process document
        const processor = new ForeclosureDocumentProcessor();
        const result = await processor.processDocument(fileName, documentType);

        // Return results
        res.json({
            success: true,
            documentId: fileName,
            urgencyScore: result.structuredData.urgencyScore,
            actionItems: result.actionItems,
            extractedData: result.structuredData,
            message: 'Document processed successfully',
        });
    } catch (error) {
        console.error('Document processing error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process document',
        });
    }
});

// Cloud Function export
exports.processForeclosureDocument = async (req, res) => {
    await app(req, res);
};

module.exports = ForeclosureDocumentProcessor;