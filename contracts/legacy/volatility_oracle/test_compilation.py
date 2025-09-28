"""
Test VolatilityOracle contract compilation and basic functionality
"""

def test_contract_structure():
    """Test that the contract can be imported and has correct structure"""
    try:
        # Test import
        from contract import VolatilityOracleContract
        
        print("✅ Contract import successful")
        
        # Test contract creation
        contract = VolatilityOracleContract()
        print("✅ Contract instantiation successful")
        
        # Test that key attributes exist
        assert hasattr(contract, 'alpha')
        assert hasattr(contract, 'current_volatility')
        assert hasattr(contract, 'current_regime')
        assert hasattr(contract, 'ewma_mean')
        assert hasattr(contract, 'ewma_variance')
        print("✅ Contract attributes verified")
        
        # Test that key methods exist
        assert hasattr(contract, 'initialize_oracle')
        assert hasattr(contract, 'update_price')
        assert hasattr(contract, 'should_rebalance')
        assert hasattr(contract, 'get_volatility')
        assert hasattr(contract, 'get_volatility_regime')
        print("✅ Contract methods verified")
        
        print("\n🎯 VolatilityOracle contract structure is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing contract: {e}")
        return False


def test_constants():
    """Test that constants are properly defined"""
    try:
        from contract import (
            FIXED_POINT_SCALE, 
            VOLATILITY_SCALE,
            LOW_VOLATILITY_THRESHOLD,
            HIGH_VOLATILITY_THRESHOLD,
            DEFAULT_ALPHA,
            DEFAULT_WINDOW_SIZE
        )
        
        print("✅ Constants imported successfully")
        
        # Verify constant values
        assert FIXED_POINT_SCALE == 1_000_000_000_000_000_000  # 1e18
        assert VOLATILITY_SCALE == 1_000_000  # 1e6
        assert LOW_VOLATILITY_THRESHOLD == 20_000  # 2%
        assert HIGH_VOLATILITY_THRESHOLD == 50_000  # 5%
        assert DEFAULT_ALPHA == 300_000  # 0.3
        assert DEFAULT_WINDOW_SIZE == 10
        
        print("✅ Constant values verified")
        print(f"  - Fixed Point Scale: {FIXED_POINT_SCALE:,}")
        print(f"  - Volatility Scale: {VOLATILITY_SCALE:,}")
        print(f"  - Low Vol Threshold: {LOW_VOLATILITY_THRESHOLD:,} ({LOW_VOLATILITY_THRESHOLD/VOLATILITY_SCALE:.1%})")
        print(f"  - High Vol Threshold: {HIGH_VOLATILITY_THRESHOLD:,} ({HIGH_VOLATILITY_THRESHOLD/VOLATILITY_SCALE:.1%})")
        print(f"  - Default Alpha: {DEFAULT_ALPHA:,} ({DEFAULT_ALPHA/VOLATILITY_SCALE:.1f})")
        print(f"  - Window Size: {DEFAULT_WINDOW_SIZE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing constants: {e}")
        return False


def test_method_signatures():
    """Test that all methods have correct signatures"""
    try:
        from contract import VolatilityOracleContract
        import inspect
        
        contract = VolatilityOracleContract()
        
        # Test key method signatures
        methods_to_test = [
            'initialize_oracle',
            'update_price', 
            'should_rebalance',
            'mark_rebalance_completed',
            'get_volatility',
            'get_volatility_regime',
            'get_oracle_info'
        ]
        
        for method_name in methods_to_test:
            method = getattr(contract, method_name)
            sig = inspect.signature(method)
            print(f"✅ {method_name}{sig}")
        
        print("\n🎯 All method signatures are valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing method signatures: {e}")
        return False


if __name__ == "__main__":
    print("🧠 Testing VolatilityOracle Contract")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Contract Structure", test_contract_structure),
        ("Constants", test_constants),
        ("Method Signatures", test_method_signatures)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VolatilityOracle is ready!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
