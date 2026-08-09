import generate_data
import preprocess
import train

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1/3  Generate synthetic telco dataset")
    print("=" * 60)
    generate_data.main()

    print("\n" + "=" * 60)
    print("STEP 2/3  Clean dataset")
    print("=" * 60)
    preprocess.main()

    print("\n" + "=" * 60)
    print("STEP 3/3  Train models, tune, evaluate, explain (SHAP)")
    print("=" * 60)
    train.run_training()

    print("\nAll pipeline steps completed.")
