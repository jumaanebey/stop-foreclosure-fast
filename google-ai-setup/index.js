/**
 * Simple Cloud Function Entry Point
 * Exports all the AI functions for Google Cloud
 */

const express = require('express');

// Simple test function first
exports.helloWorld = (req, res) => {
    res.json({
        message: 'Hello from Foreclosure AI!',
        timestamp: new Date().toISOString(),
        project: 'MyForeclosureSolution.com'
    });
};

// Mock lead qualification for now
exports.qualifyForeclosureLead = (req, res) => {
    const leadData = req.body;

    // Simple scoring logic
    let urgencyScore = 5;

    if (leadData.timelineUrgency && leadData.timelineUrgency.includes('days')) {
        const days = parseInt(leadData.timelineUrgency);
        if (days <= 7) urgencyScore = 10;
        else if (days <= 30) urgencyScore = 8;
        else if (days <= 60) urgencyScore = 6;
    }

    if (leadData.foreclosureStage === 'notice_of_sale') urgencyScore = 10;
    if (leadData.monthsBehind >= 6) urgencyScore += 1;

    // Generate lead ID
    const leadId = `FCL-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Respond immediately
    res.json({
        success: true,
        leadId: leadId,
        urgencyScore: Math.min(urgencyScore, 10),
        qualificationScore: 7,
        message: 'Lead processed successfully',
        nextSteps: urgencyScore >= 8 ? 'Immediate callback scheduled' : 'Response within 24 hours',
        recommendedAction: urgencyScore >= 8 ?
            'URGENT: Contact within 2 hours' :
            'Standard: Contact within 24 hours'
    });

    // Log for tracking
    console.log('Lead qualified:', { leadId, urgencyScore, leadData });
};

// Mock document processor
exports.processForeclosureDocument = (req, res) => {
    res.json({
        success: true,
        documentId: `DOC-${Date.now()}`,
        urgencyScore: 8,
        extractedData: {
            documentType: 'notice_of_default',
            amount: 12500,
            deadline: '2024-04-15'
        },
        actionItems: [
            {
                priority: 'HIGH',
                action: 'Contact homeowner immediately',
                deadline: 'Within 2 hours'
            }
        ]
    });
};

// Mock email processor
exports.processForeclosureEmail = (req, res) => {
    res.json({
        success: true,
        messageId: `EMAIL-${Date.now()}`,
        response: 'Personalized email sent successfully'
    });
};