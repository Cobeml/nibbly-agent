#!/usr/bin/env python3
"""
Test script for API calls in the hackathon agent.
Tests both Gemma API calls and ROS2 WebSocket functionality.
"""

import os
import json
import time
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Import the functions we want to test
from hackathon_agent.agent import (
    ask_gemma,
    generate_code,
    brainstorm_ideas,
    explain_concept,
    get_restaurant_options,
    create_delivery_order,
    track_order_status,
    ROSBridge,
    GemmaClient
)

class TestGemmaAPICalls(unittest.TestCase):
    """Test cases for Gemma API functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Store original environment variables
        self.original_gemma_url = os.environ.get('GEMMA_URL')
        # Set a dummy GEMMA_URL for testing
        os.environ['GEMMA_URL'] = 'https://test-gemma-url.com'
    
    def tearDown(self):
        """Restore original environment variables."""
        if self.original_gemma_url:
            os.environ['GEMMA_URL'] = self.original_gemma_url
        elif 'GEMMA_URL' in os.environ:
            del os.environ['GEMMA_URL']
    
    @patch('hackathon_agent.agent.requests.post')
    def test_ask_gemma_success(self, mock_post):
        """Test successful ask_gemma call."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'This is a test response from Gemma'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_gemma("What is AI?", "AI context")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['question'], 'What is AI?')
        self.assertEqual(result['answer'], 'This is a test response from Gemma')
        self.assertTrue(result['context_provided'])
    
    @patch('hackathon_agent.agent.requests.post')
    def test_ask_gemma_no_context(self, mock_post):
        """Test ask_gemma call without context."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Simple response'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_gemma("Simple question", "")
        
        self.assertEqual(result['status'], 'success')
        self.assertFalse(result['context_provided'])
    
    @patch('hackathon_agent.agent.requests.post')
    def test_ask_gemma_error(self, mock_post):
        """Test ask_gemma call with error."""
        # Mock the get_gemma_client to raise an exception
        with patch('hackathon_agent.agent.get_gemma_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Network error")
            
            result = ask_gemma("Test question", "")
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('error_message', result)
    
    @patch('hackathon_agent.agent.requests.post')
    def test_generate_code(self, mock_post):
        """Test generate_code function."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'def hello(): return "Hello World"'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = generate_code("Create a hello function", "Python")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['language'], 'Python')
        self.assertEqual(result['description'], 'Create a hello function')
    
    @patch('hackathon_agent.agent.requests.post')
    def test_brainstorm_ideas(self, mock_post):
        """Test brainstorm_ideas function."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': '1. Idea 1\n2. Idea 2'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = brainstorm_ideas("AI applications", 2)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['topic'], 'AI applications')
        self.assertEqual(result['requested_ideas'], 2)
    
    @patch('hackathon_agent.agent.requests.post')
    def test_explain_concept(self, mock_post):
        """Test explain_concept function."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Machine learning is...'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = explain_concept("Machine Learning", "beginner")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['concept'], 'Machine Learning')
        self.assertEqual(result['level'], 'beginner')


class TestROSBridge(unittest.TestCase):
    """Test cases for ROSBridge WebSocket functionality."""
    
    @patch('hackathon_agent.agent.websocket.create_connection')
    def test_rosbridge_connection(self, mock_create_connection):
        """Test ROSBridge connection."""
        mock_ws = MagicMock()
        mock_create_connection.return_value = mock_ws
        
        bridge = ROSBridge("ws://test-url")
        
        mock_create_connection.assert_called_once_with("ws://test-url", timeout=10)
        self.assertIsNotNone(bridge.ws)
    
    @patch('hackathon_agent.agent.websocket.create_connection')
    def test_rosbridge_publish(self, mock_create_connection):
        """Test ROSBridge publish method."""
        mock_ws = MagicMock()
        mock_create_connection.return_value = mock_ws
        
        bridge = ROSBridge("ws://test-url")
        bridge.publish("/test/topic", "std_msgs/String", {"data": "test"})
        
        expected_data = {
            "op": "publish",
            "topic": "/test/topic",
            "type": "std_msgs/String",
            "msg": {"data": "test"}
        }
        mock_ws.send.assert_called_once_with(json.dumps(expected_data))
    
    @patch('hackathon_agent.agent.websocket.create_connection')
    def test_rosbridge_subscribe_and_receive(self, mock_create_connection):
        """Test ROSBridge subscribe and receive method."""
        mock_ws = MagicMock()
        mock_ws.recv.side_effect = [
            json.dumps({
                "op": "publish",
                "topic": "/test/topic",
                "msg": {"data": "test response"}
            })
        ]
        mock_create_connection.return_value = mock_ws
        
        bridge = ROSBridge("ws://test-url")
        result = bridge.subscribe_and_receive("/test/topic", timeout=5)
        
        expected_subscribe = {
            "op": "subscribe",
            "topic": "/test/topic"
        }
        mock_ws.send.assert_called_with(json.dumps(expected_subscribe))
        self.assertEqual(result, {"data": "test response"})


class TestDeliveryAPICalls(unittest.TestCase):
    """Test cases for delivery API functionality."""
    
    @patch('hackathon_agent.agent.ROSBridge')
    def test_get_restaurant_options_success(self, mock_rosbridge_class):
        """Test successful get_restaurant_options call."""
        mock_bridge = MagicMock()
        mock_rosbridge_class.return_value = mock_bridge
        
        mock_bridge.subscribe_and_receive.return_value = {
            "data": json.dumps({
                "restaurants": [
                    {"id": "1", "name": "Pizza Place", "menu": ["pizza", "pasta"]}
                ]
            })
        }
        
        result = get_restaurant_options()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('restaurant_data', result)
        mock_bridge.publish.assert_called_once_with(
            '/delivery/restaurant_request', 
            'std_msgs/String', 
            {'data': ''}
        )
        mock_bridge.subscribe_and_receive.assert_called_once_with('/delivery/restaurant_data')
        mock_bridge.close.assert_called_once()
    
    @patch('hackathon_agent.agent.ROSBridge')
    def test_get_restaurant_options_error(self, mock_rosbridge_class):
        """Test get_restaurant_options call with error."""
        mock_rosbridge_class.side_effect = Exception("Connection failed")
        
        result = get_restaurant_options()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error_message', result)
    
    @patch('hackathon_agent.agent.ROSBridge')
    def test_create_delivery_order_success(self, mock_rosbridge_class):
        """Test successful create_delivery_order call."""
        mock_bridge = MagicMock()
        mock_rosbridge_class.return_value = mock_bridge
        
        delivery_location = {"lat": 37.7749, "lng": -122.4194}
        items = ["pizza", "soda"]
        
        result = create_delivery_order(
            restaurant_id="rest_123",
            customer_name="John Doe",
            delivery_location=delivery_location,
            items=items,
            priority=2,
            special_instructions="Extra cheese please"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('order_id', result)
        self.assertIn('order_details', result)
        self.assertEqual(result['order_details']['restaurant_id'], 'rest_123')
        self.assertEqual(result['order_details']['customer_name'], 'John Doe')
        self.assertEqual(result['order_details']['items'], items)
        
        # Verify the order was published
        mock_bridge.publish.assert_called_once()
        call_args = mock_bridge.publish.call_args
        self.assertEqual(call_args[0][0], '/delivery/order_request')
        self.assertEqual(call_args[0][1], 'std_msgs/String')
        
        # Verify the order data structure
        order_data = json.loads(call_args[0][2]['data'])
        self.assertEqual(order_data['restaurant_id'], 'rest_123')
        self.assertEqual(order_data['customer_name'], 'John Doe')
        self.assertEqual(order_data['items'], items)
        self.assertEqual(order_data['priority'], 2)
        self.assertEqual(order_data['special_instructions'], 'Extra cheese please')
    
    @patch('hackathon_agent.agent.ROSBridge')
    def test_track_order_status_success(self, mock_rosbridge_class):
        """Test successful track_order_status call."""
        mock_bridge = MagicMock()
        mock_rosbridge_class.return_value = mock_bridge
        
        # Mock the status response
        mock_bridge.subscribe_and_receive.return_value = {
            "data": json.dumps({
                "current_order_id": "AI-1234567890",
                "status": "in_progress",
                "estimated_delivery": "2024-01-15T14:30:00Z"
            })
        }
        
        result = track_order_status("AI-1234567890", duration=10)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['order_id'], 'AI-1234567890')
        self.assertIn('order_status', result)
        
        # Verify the status was checked
        mock_bridge.subscribe_and_receive.assert_called_with('/delivery/status', timeout=5)
        mock_bridge.close.assert_called_once()
    
    @patch('hackathon_agent.agent.ROSBridge')
    def test_track_order_status_timeout(self, mock_rosbridge_class):
        """Test track_order_status call with timeout."""
        mock_bridge = MagicMock()
        mock_rosbridge_class.return_value = mock_bridge
        
        # Mock timeout scenario
        mock_bridge.subscribe_and_receive.return_value = {
            "data": json.dumps({
                "current_order_id": "different_order_id",
                "status": "in_progress"
            })
        }
        
        result = track_order_status("AI-1234567890", duration=1)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('timeout', result['error_message'])


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test environment."""
        # Store original environment variables
        self.original_gemma_url = os.environ.get('GEMMA_URL')
        self.original_ros2_url = os.environ.get('ROS2_WS_URL')
        
        # Set test environment variables
        os.environ['GEMMA_URL'] = 'https://test-gemma-url.com'
        os.environ['ROS2_WS_URL'] = 'wss://a78a6101be74.ngrok-free.app'
    
    def tearDown(self):
        """Restore original environment variables."""
        if self.original_gemma_url:
            os.environ['GEMMA_URL'] = self.original_gemma_url
        elif 'GEMMA_URL' in os.environ:
            del os.environ['GEMMA_URL']
            
        if self.original_ros2_url:
            os.environ['ROS2_WS_URL'] = self.original_ros2_url
        elif 'ROS2_WS_URL' in os.environ:
            del os.environ['ROS2_WS_URL']
    
    def test_environment_variables(self):
        """Test that environment variables are properly set."""
        # Import after setting environment variables
        import importlib
        import hackathon_agent.agent
        importlib.reload(hackathon_agent.agent)
        
        from hackathon_agent.agent import GEMMA_URL, ROS2_WS_URL
        
        self.assertEqual(GEMMA_URL, 'https://test-gemma-url.com')
        self.assertEqual(ROS2_WS_URL, 'wss://a78a6101be74.ngrok-free.app')
    
    @patch('hackathon_agent.agent.requests.post')
    @patch('hackathon_agent.agent.ROSBridge')
    def test_full_delivery_workflow(self, mock_rosbridge_class, mock_post):
        """Test a complete delivery workflow."""
        # Mock Gemma response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Here are some restaurant recommendations'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Mock ROSBridge
        mock_bridge = MagicMock()
        mock_rosbridge_class.return_value = mock_bridge
        
        # Mock restaurant data
        mock_bridge.subscribe_and_receive.side_effect = [
            {"data": json.dumps({"restaurants": [{"id": "1", "name": "Test Restaurant"}]})},
            {"data": json.dumps({"current_order_id": "AI-123", "status": "confirmed"})}
        ]
        
        # Test the workflow
        restaurants = get_restaurant_options()
        self.assertEqual(restaurants['status'], 'success')
        
        order = create_delivery_order(
            restaurant_id="1",
            customer_name="Test User",
            delivery_location={"lat": 37.7749, "lng": -122.4194},
            items=["pizza"]
        )
        self.assertEqual(order['status'], 'success')
        
        # Mock the second call to subscribe_and_receive for status tracking
        mock_bridge.subscribe_and_receive.side_effect = [
            {"data": json.dumps({"restaurants": [{"id": "1", "name": "Test Restaurant"}]})},
            {"data": json.dumps({"current_order_id": order['order_id'], "status": "confirmed"})}
        ]
        
        status = track_order_status(order['order_id'])
        self.assertEqual(status['status'], 'success')


def run_live_tests():
    """Run live tests against the actual ngrok endpoint."""
    print("\n" + "="*60)
    print("RUNNING LIVE TESTS AGAINST NGROK ENDPOINT")
    print("="*60)
    
    # Test ROSBridge connection
    print("\n1. Testing ROSBridge connection...")
    try:
        bridge = ROSBridge("wss://a78a6101be74.ngrok-free.app")
        print("✅ ROSBridge connection successful")
        bridge.close()
    except Exception as e:
        print(f"❌ ROSBridge connection failed: {e}")
    
    # Test restaurant options
    print("\n2. Testing get_restaurant_options...")
    try:
        result = get_restaurant_options()
        print(f"Result: {result}")
        if result['status'] == 'success':
            print("✅ get_restaurant_options successful")
        else:
            print(f"❌ get_restaurant_options failed: {result.get('error_message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ get_restaurant_options exception: {e}")
    
    # Test order creation
    print("\n3. Testing create_delivery_order...")
    try:
        result = create_delivery_order(
            restaurant_id="test_restaurant",
            customer_name="Test Customer",
            delivery_location={"lat": 37.7749, "lng": -122.4194},
            items=["pizza", "soda"],
            priority=2,
            special_instructions="Test order"
        )
        print(f"Result: {result}")
        if result['status'] == 'success':
            print("✅ create_delivery_order successful")
            order_id = result['order_id']
            
            # Test order tracking
            print("\n4. Testing track_order_status...")
            try:
                status_result = track_order_status(order_id, duration=10)
                print(f"Status result: {status_result}")
                if status_result['status'] == 'success':
                    print("✅ track_order_status successful")
                else:
                    print(f"⚠️ track_order_status: {status_result.get('error_message', 'Unknown error')}")
            except Exception as e:
                print(f"❌ track_order_status exception: {e}")
        else:
            print(f"❌ create_delivery_order failed: {result.get('error_message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ create_delivery_order exception: {e}")


if __name__ == '__main__':
    print("Starting API Tests...")
    
    # Run unit tests
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run live tests
    run_live_tests()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60) 